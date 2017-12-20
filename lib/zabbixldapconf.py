import configparser
import sys
import traceback

from ldapconn import LDAPConn


class ZabbixLDAPConf(object):
    """
    Zabbix-LDAP configuration class

    Provides methods for parsing and retrieving config entries

    """

    def __init__(self, config):
        self.config = config

    def try_get_item(self, parser, section, option, default):
        """
        Gets config item

        Args:
            parser  (ConfigParser): ConfigParser
            section          (str): Config section name
            option           (str): Config option name
            default               : Value to return if item doesn't exist

        Returns:
            Config item value or default value

        """

        try:
            result = parser.get(section, option)
        except (configparser.NoOptionError, configparser.NoSectionError):
            result = default

        return result

    def try_get_section(self, parser, section, default):
        """
        Gets config section

        Args:
            parser  (ConfigParser): ConfigParser
            section          (str): Config section name
            default               : Value to return if section doesn't exist

        Returns:
            Config section dict or default value

        """

        try:
            result = parser.items(section)
        except configparser.NoSectionError:
            result = default

        return result

    def remove_config_section_items(self, section, items):
        """
        Removes items from config section

        Args:
            section     (list of tuples): Config section
            items                 (list): Item names to remove

        Returns:
            Config section without specified items

        """

        return [i for i in section if i[0] not in items]

    def load_config(self):
        """
        Loads the configuration file

        Raises:
            ConfigParser.NoOptionError

        """
        parser = configparser.ConfigParser()
        parser.read(self.config)

        try:
            self.ldap_type = self.try_get_item(parser, 'ldap', 'type', None)

            self.ldap_uri = parser.get('ldap', 'uri')
            self.ldap_base = parser.get('ldap', 'base')

            self.ldap_groups = [i.strip() for i in parser.get('ldap', 'groups').split(',')]

            self.ldap_user = parser.get('ldap', 'binduser')
            self.ldap_pass = parser.get('ldap', 'bindpass')

            self.ldap_media = self.try_get_item(parser, 'ldap', 'media', 'mail')

            self.ad_filtergroup = parser.get('ad', 'filtergroup', fallback='(&(objectClass=group)(name=%s))', raw=True)
            self.ad_filteruser = parser.get('ad', 'filteruser', fallback='(objectClass=user)(objectCategory=Person))',
                                            raw=True)
            self.ad_filterdisabled = parser.get('ad', 'filterdisabled',
                                                fallback='(!(userAccountControl:1.2.840.113556.1.4.803:=2))', raw=True)
            self.ad_filtermemberof = parser.get('ad', 'filtermemberof',
                                                fallback='(memberOf:1.2.840.113556.1.4.1941:=%s)', raw=True)
            self.ad_groupattribute = parser.get('ad', 'groupattribute', fallback='member', raw=True)
            self.ad_userattribute = parser.get('ad', 'userattribute', fallback='sAMAccountName', raw=True)

            self.openldap_type = parser.get('openldap', 'type', fallback='posixgroup')
            self.openldap_filtergroup = parser.get('openldap', 'filtergroup',
                                                   fallback='(&(objectClass=posixGroup)(cn=%s))', raw=True)
            self.openldap_filteruser = parser.get('openldap', 'filteruser',
                                                  fallback='(&(objectClass=posixAccount)(uid=%s))', raw=True)
            self.openldap_groupattribute = parser.get('openldap', 'groupattribute', fallback='memberUid', raw=True)
            self.openldap_userattribute = parser.get('openldap', 'userattribute', fallback='uid', raw=True)

            self.zbx_server = parser.get('zabbix', 'server')
            self.zbx_username = parser.get('zabbix', 'username')
            self.zbx_password = parser.get('zabbix', 'password')
            self.zbx_auth = parser.get('zabbix', 'auth')

            self.user_opt = self.try_get_section(parser, 'user', {})

            self.media_description = self.try_get_item(parser, 'media', 'description', 'Email')
            self.media_opt = self.remove_config_section_items(self.try_get_section(parser, 'media', {}),
                                                              ('description', 'userid'))

        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stderr)
            raise SystemExit('Configuration issues detected in %s' % self.config)

    def set_groups_with_wildcard(self):
        """
        Set group from LDAP with wildcard
        :return:
        """
        result_groups = []
        ldap_conn = LDAPConn(self.ldap_uri, self.ldap_base, self.ldap_user, self.ldap_pass)
        ldap_conn.connect()

        for group in self.ldap_groups:
            groups = ldap_conn.get_groups_with_wildcard(group)
            result_groups = result_groups + groups

        if result_groups:
            self.ldap_groups = result_groups
        else:
            raise SystemExit('ERROR - No groups found with wildcard')
