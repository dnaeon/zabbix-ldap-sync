import ldap
import ldap.filter


class LDAPConn(object):
    """
    LDAP connector class

    Defines methods for retrieving users and groups from LDAP server.

    """

    def __init__(self, config):
        self.uri = config.ldap_uri
        self.base = config.ldap_base
        self.ldap_user = config.ldap_user
        self.ldap_pass = config.ldap_passwd
        self.group_member_attribute = config.ldap_group_member_attribute
        self.group_filter = config.ldap_group_filter
        #self.active_directory = config.ldap_active_directory
        self.uid_attribute = config.ldap_uid_attribute
        self.recursive = config.ldap_recursive
        self.memberof_filter = config.ldap_memberof_filter
        self.skipdisabled = config.ldap_skipdisabled
        self.lowercase = config.ldap_lowercase
        self.user_filter = config.ldap_user_filter
        self.active_directory = config.ldap_active_directory

    def connect(self):
        """
        Establish a connection to the LDAP server.

        Raises:
            SystemExit

        """
        self.conn = ldap.initialize(self.uri)
        self.conn.set_option(ldap.OPT_REFERRALS, ldap.OPT_OFF)

        try:
            self.conn.simple_bind_s(self.ldap_user, self.ldap_pass)
        except ldap.SERVER_DOWN as e:
            raise SystemExit('Cannot connect to LDAP server: %s' % e)

    def disconnect(self):
        """
        Disconnect from the LDAP server.

        """
        self.conn.unbind()

    def remove_ad_referrals(self, result):
        """
        Remove referrals from AD query result

        """
        return [i for i in result if i[0] != None]

    def get_group_members(self, group):
        """
        Retrieves the members of an LDAP group

        Args:
            group (str): The LDAP group name

        Returns:
            A list of all users in the LDAP group

        """
        attrlist = [self.group_member_attribute]
        filter = self.group_filter % group

        result = self.conn.search_s(base=self.base,
                                    scope=ldap.SCOPE_SUBTREE,
                                    filterstr=filter,
                                    attrlist=attrlist)

        if not result:
            print('>>> Unable to find group "%s" with filter "%s", skipping group' % (group, filter))
            return None


        # Get DN for each user in the group
        if self.active_directory:

            result = self.remove_ad_referrals(result)

            final_listing = {}

            for members in result:
                result_dn = members[0]
                result_attrs = members[1]

            group_members = []
            attrlist = [self.uid_attribute]

            if self.recursive:
                # Get a DN for all users in a group (recursive)
                # It's available only on domain controllers with Windows Server 2003 SP2 or later

                member_of_filter_dn = self.memberof_filter % result_dn

                if self.skipdisabled:
                    filter = "(&%s%s%s)" % (self.user_filter, member_of_filter_dn, self.disabled_filter)
                else:
                    filter = "(&%s%s)" % (self.user_filter, member_of_filter_dn)

                uid = self.conn.search_s(base=self.base,
                                         scope=ldap.SCOPE_SUBTREE,
                                         filterstr=filter,
                                         attrlist=attrlist)

                for item in self.remove_ad_referrals(uid):
                    group_members.append(item)
            else:
                # Otherwise, just get a DN for each user in the group
                for member in result_attrs[self.group_member_attribute]:
                    if self.skipdisabled:
                        filter = "(&%s%s)" % (self.user_filter, self.disabled_filter)
                    else:
                        filter = "(&%s)" % self.user_filter

                    uid = self.conn.search_s(base=member.decode('utf8'),
                                             scope=ldap.SCOPE_BASE,
                                             filterstr=filter,
                                             attrlist=attrlist)
                    for item in uid:
                        group_members.append(item)

            # Fill dictionary with usernames and corresponding DNs
            for item in group_members:
                dn = item[0]
                username = item[1][self.uid_attribute]

                if self.lowercase:
                    username = username[0].decode('utf8').lower()
                else:
                    username = username[0].decode('utf8')

                final_listing[username] = dn

            return final_listing

        else:

            dn, users = result.pop()

            final_listing = {}

            group_members = []

            # Get info for each user in the group
            for memberid in users[self.group_member_attribute]:

                if self.openldap_type == "groupofnames":

                    filter = "(objectClass=*)"
                    # memberid is user dn
                    base = memberid

                else:

                    # memberid is user attribute, most likely uid
                    filter = self.user_filter % memberid
                    base = self.base

                attrlist = [self.uid_attribute]

                # get the actual LDAP object for each group member
                uid = self.conn.search_s(base=base,
                                         scope=ldap.SCOPE_SUBTREE,
                                         filterstr=filter,
                                         attrlist=attrlist)

                for item in uid:
                    group_members.append(item)

                # Fill dictionary with usernames and corresponding DNs
                for item in group_members:
                    dn = item[0]
                    username = item[1][self.uid_attribute]
                    user = ''.join(username)

                final_listing[user] = dn

            return final_listing

    def get_groups_with_wildcard(self, groups_wildcard):
        print(">>> Search group with wildcard: %s" % groups_wildcard)

        filter = self.group_filter % groups_wildcard
        result_groups = []

        result = self.conn.search_s(base=self.base,
                                    scope=ldap.SCOPE_SUBTREE,
                                    filterstr=filter, )

        for group in result:
            # Skip refldap (when Active Directory used)
            # [0]==None
            if group[0]:
                group_name = group[1]['name'][0]
                print("Find group %s" % group_name)
                result_groups.append(group_name)

        if not result_groups:
            print('>>> Unable to find group "%s", skipping group wildcard' % groups_wildcard)

        return result_groups

    def get_user_media(self, dn, ldap_media):
        """
        Retrieves the 'media' attribute of an LDAP user

        Args:
            username (str): The LDAP distinguished name to lookup
            ldap_media (str): The name of the field containing the media address

        Returns:
            The user's media attribute value

        """
        attrlist = [ldap_media]

        result = self.conn.search_s(base=dn,
                                    scope=ldap.SCOPE_BASE,
                                    attrlist=attrlist)

        if not result:
            return None

        dn, data = result.pop()

        mail = data.get(ldap_media)

        if not mail:
            return None

        return mail.pop()

    def get_user_sn(self, dn):
        """
        Retrieves the 'sn' attribute of an LDAP user

        Args:
            username (str): The LDAP distinguished name to lookup

        Returns:
            The user's surname attribute

        """
        attrlist = ['sn']

        result = self.conn.search_s(base=dn,
                                    scope=ldap.SCOPE_BASE,
                                    attrlist=attrlist)

        if not result:
            return None

        dn, data = result.pop()

        sn = data.get('sn')

        if not sn:
            return None

        return sn.pop()

    def get_user_givenName(self, dn):
        """
        Retrieves the 'givenName' attribute of an LDAP user

        Args:
            username (str): The LDAP distinguished name to lookup

        Returns:
            The user's given name attribute

        """
        attrlist = ['givenName']

        result = self.conn.search_s(base=dn,
                                    scope=ldap.SCOPE_BASE,
                                    attrlist=attrlist)

        if not result:
            return None

        dn, data = result.pop()

        name = data.get('givenName')

        if not name:
            return None

        return name.pop()
