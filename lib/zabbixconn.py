import logging
import random
import string
import collections
import re

from pyzabbix import ZabbixAPI, ZabbixAPIException


class ZabbixConn(object):
    """
    Zabbix connector class

    Defines methods for managing Zabbix users and groups

    """

    def __init__(self, server, username, password, auth, ldap_conn, config, dryrun):
        self.server = server
        self.username = username
        self.password = password
        self.auth = auth
        self.ldap_conn = ldap_conn
        self.config = config
        self.dryrun = dryrun

    def verbose(self):
        # Use logger to log information
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Log to stdout
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)  # Use logger to log information

        # Log from pyzabbix
        log = logging.getLogger('pyzabbix')
        log.addHandler(ch)
        log.setLevel(logging.DEBUG)

    def connect(self, nocheckcertificate):
        """
        Establishes a connection to the Zabbix server

        Args:
            nocheckcertificate (bool): Don't check the server certificate

        Raises:
            SystemExit

        """

        if self.auth == "webform":
            self.conn = ZabbixAPI(self.server)
        elif self.auth == "http":
            self.conn = ZabbixAPI(self.server, use_authenticate=False)
            self.conn.session.auth = (self.username, self.password)

        else:
            raise SystemExit('api auth method not implemented: %s' % self.conn.auth)

        if nocheckcertificate:
            self.conn.session.verify = False

        try:
            self.conn.login(self.username, self.password)
        except ZabbixAPIException as e:
            raise SystemExit('Cannot login to Zabbix server: %s' % e)

        print("Connected to Zabbix API Version %s" % self.conn.api_version())

    def get_users(self):
        """
        Retrieves the existing Zabbix users

        Returns:
            A list of the existing Zabbix users

        """
        result = self.conn.user.get(output='extend')

        users = [user['alias'] for user in result]

        return users

    def get_mediatype_id(self, description):
        """
        Retrieves the mediatypeid by description

        Args:
            description (str): Zabbix media type description

        Returns:
            The mediatypeid for specified media type description

        """
        result = self.conn.mediatype.get(filter={'description': description})

        if result:
            mediatypeid = result[0]['mediatypeid']
        else:
            mediatypeid = None

        return mediatypeid

    def get_user_id(self, user):
        """
        Retrieves the userid of a specified user

        Args:
            user (str): The Zabbix username to lookup

        Returns:
            The userid of the specified user

        """
        result = self.conn.user.get(output='extend')

        userid = [u['userid'] for u in result if u['alias'] == user].pop()

        return userid

    def get_groups(self):
        """
        Retrieves the existing Zabbix groups

        Returns:
            A dict of the existing Zabbix groups and their group ids

        """
        result = self.conn.usergroup.get(status=0, output='extend')

        groups = [{'name': group['name'], 'usrgrpid': group['usrgrpid']} for group in result]

        return groups

    def get_group_members(self, groupid):
        """
        Retrieves group members for a Zabbix group

        Args:
            groupid (int): The group id

        Returns:
            A list of the Zabbix users for the specified group id

        """
        result = self.conn.user.get(output='extend', usrgrpids=groupid)

        users = [user['alias'] for user in result]

        return users

    def create_group(self, group):
        """
        Creates a new Zabbix group

        Args:
            group (str): The Zabbix group name to create

        Returns:
            The groupid of the newly created group

        """
        result = self.conn.usergroup.create(name=group)

        groupid = result['usrgrpids'].pop()

        return groupid

    def create_user(self, user, groupid, user_opt):
        """
        Creates a new Zabbix user

        Args:
            user     (dict): A dict containing the user details
            groupid   (int): The groupid for the new user
            user_opt (dict): User options

        """
        random_passwd = ''.join(random.sample(string.ascii_letters + string.digits, 32))

        user_defaults = {'autologin': 0, 'type': 1, 'usrgrps': [{'usrgrpid': str(groupid)}], 'passwd': random_passwd}
        user_defaults.update(user_opt)
        user.update(user_defaults)

        result = self.conn.user.create(user)

        return result

    def delete_user(self, user):
        """
        Deletes Zabbix user

        Args:
            user (string): Zabbix username

        """
        userid = self.get_user_id(user)

        result = self.conn.user.delete(userid)

        return result

    def update_user(self, user, groupid):
        """
        Adds an existing Zabbix user to a group

        Args:
            user    (dict): A dict containing the user details
            groupid  (int): The groupid to add the user to

        """
        userid = self.get_user_id(user)

        result = self.conn.usergroup.massadd(usrgrpids=[str(groupid)], userids=[str(userid)])

        return result

    def update_media(self, user, description, sendto, media_opt):
        """
        Adds media to an existing Zabbix user

        Args:
            user        (dict): A dict containing the user details
            description  (str): A string containing Zabbix media description
            sendto       (str): A string containing address, phone number, etc...
            media_opt    (dict): Media options

        """

        userid = self.get_user_id(user)
        mediatypeid = self.get_mediatype_id(description)

        if mediatypeid:
            media_defaults = {
                'mediatypeid': mediatypeid,
                'sendto': sendto,
                'active': '0',
                'severity': '63',
                'period': '1-7,00:00-24:00'
            }
            media_defaults.update(media_opt)

            self.delete_media_by_description(user, description)
            result = self.conn.user.addmedia(users=[{"userid": str(userid)}], medias=media_defaults)
        else:
            result = None

        return result

    def delete_media_by_description(self, user, description):
        """
        Remove all media from user (with specific mediatype)

        Args:
            user        (dict): A dict containing the user details
            description  (str): A string containing Zabbix media description

        """

        userid = self.get_user_id(user)
        mediatypeid = self.get_mediatype_id(description)

        if mediatypeid:
            user_full = self.conn.user.get(output="extend", userids=userid, selectMedias=["mediatypeid", "mediaid"])
            media_ids = [int(u['mediaid']) for u in user_full[0]['medias'] if u['mediatypeid'] == mediatypeid]

            if media_ids:
                print('>>> Remove other exist media from user %s (type=%s)' % (user, description))
                for id in media_ids:
                    self.conn.user.deletemedia(id)

    def create_missing_groups(self, ldap_groups):
        """
        Creates any missing LDAP groups in Zabbix

        Args:
            ldap_groups (list): A list of LDAP groups to create

        """
        missing_groups = set(ldap_groups) - set([g['name'] for g in self.get_groups()])

        for eachGroup in missing_groups:
            print('>>> Creating Zabbix group %s' % eachGroup)
            if not self.dryrun:
                grpid = self.create_group(eachGroup)
                print('>>> Group %s created with groupid %s' % (eachGroup, grpid))

    def convert_severity(self, severity):

        if re.match("\d+", severity):
            return severity

        sev_entries = collections.OrderedDict({
            "Disaster": "0",
            "High": "0",
            "Average": "0",
            "Warning": "0",
            "Information": "0",
            "Not Classified": "0",
        })

        for sev in severity.split(","):
            sev = sev.strip()
            if sev not in sev_entries:
                raise Exception("wrong argument: %s" % sev)
            sev_entries[sev] = "1"

        str_bitmask = ""
        for sev, digit in sev_entries.items():
            str_bitmask += digit

        severity = str(int(str_bitmask, 2))

        return severity

    def sync_users(self, user_opt, media_description, media_opt):
        """
        Syncs Zabbix with LDAP users
        """

        self.ldap_conn.connect()
        zabbix_all_users = self.get_users()

        for eachGroup in self.config.ldap_groups:

            ldap_users = self.ldap_conn.get_group_members(eachGroup)

            # Do nothing if LDAP group contains no users and "--delete-orphans" is not specified
            if not ldap_users and not self.deleteorphans:
                continue

            zabbix_grpid = [g['usrgrpid'] for g in self.get_groups() if g['name'] == eachGroup].pop()

            zabbix_group_users = self.get_group_members(zabbix_grpid)

            missing_users = set(list(ldap_users.keys())) - set(zabbix_group_users)

            # Add missing users
            for eachUser in missing_users:

                # Create new user if it does not exists already
                if eachUser not in zabbix_all_users:
                    print('>>> Creating user "%s", member of Zabbix group "%s"' % (eachUser, eachGroup))
                    user = {'alias': eachUser}
                    user['name'] = self.ldap_conn.get_user_givenName(ldap_users[eachUser]).decode('utf8')
                    user['surname'] = self.ldap_conn.get_user_sn(ldap_users[eachUser]).decode('utf8')

                    if user['name'] is None:
                        user['name'] = ''
                    if user['surname'] is None:
                        user['surname'] = ''

                    self.create_user(user, zabbix_grpid, user_opt)
                    zabbix_all_users.append(eachUser)
                else:
                    # Update existing user to be member of the group
                    print('>>> Updating user "%s", adding to group "%s"' % (eachUser, eachGroup))
                    self.update_user(eachUser, zabbix_grpid)

            # Handle any extra users in the groups
            extra_users = set(zabbix_group_users) - set(list(ldap_users.keys()))
            if extra_users:
                print('>>> Users in group %s which are not found in LDAP group:' % eachGroup)

                for eachUser in extra_users:
                    if self.deleteorphans:
                        print('Deleting user: "%s"' % eachUser)
                        if not self.dryrun:
                            self.delete_user(eachUser)
                    else:
                        print(' * %s' % eachUser)

            # update users media
            onlycreate = False
            media_opt_filtered = []
            for elem in media_opt:
                if elem[0] == "onlycreate" and elem[1].lower() == "true":
                    onlycreate = True
                if elem[0] == "severity":
                    media_opt_filtered.append(
                        (elem[0], self.convert_severity(elem[1]))
                    )
                else:
                    media_opt_filtered.append(elem)

            if onlycreate:
                print("Add media only on newly created users for group >>>%s<<<" % eachGroup)
                zabbix_group_users = missing_users
            else:
                print("Update media on all users for group >>>%s<<<" % eachGroup)
                zabbix_group_users = self.get_group_members(zabbix_grpid)

            for eachUser in set(zabbix_group_users):
                print('>>> Updating/create user media for "%s", update "%s"' % (eachUser, media_description))
                sendto = self.ldap_conn.get_user_media(ldap_users[eachUser], self.config.ldap_media).decode("utf8")

                if sendto and not self.dryrun:
                    self.update_media(eachUser, media_description, sendto, media_opt_filtered)

        self.ldap_conn.disconnect()
