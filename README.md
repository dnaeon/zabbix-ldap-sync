## zabbix-ldap-sync -- Sync your Zabbix users with LDAP directory server

The *zabbix-ldap-sync* script is used for keeping your Zabbix users in sync with an LDAP directory server.

It can automatically import existing LDAP groups and users into Zabbix, thus making it easy for you to keep your Zabbix users in sync with LDAP.

## Requirements

* Python 2.7.x
* [python-ldap](https://pypi.python.org/pypi/python-ldap/)
* [pyzabbix](https://github.com/lukecyca/pyzabbix)
* [docopt](https://github.com/docopt/docopt)

You also need to have your Zabbix Frontend configured to authenticate against an AD/LDAP directory server.

Check the official documentation of Zabbix on how to 
[configure Zabbix to authenticate against an AD/LDAP directory server](https://www.zabbix.com/documentation/2.2/manual/web_interface/frontend_sections/administration/authentication).

## Configuration

In order to use the *zabbix-ldap-sync* script we need to create a configuration file describing the various LDAP and Zabbix related config entries:

	[ldap]
	uri = ldaps://ldap.example.org:636/
	base = dc=example,dc=org
	binduser = DOMAIN\ldapuser
	bindpass = ldappass
	groups = sysadmins

	[zabbix]
	server = http://zabbix.example.org/zabbix/
	username = admin
	password = adminp4ssw0rd

## Importing LDAP users into Zabbix

Now that we have the above mentioned configuration file created, let's import our groups and users from LDAP to Zabbix.

	$ zabbix-ldap-sync -f /path/to/zabbix-ldap.conf
	
Once the script completes, check your Zabbix Frontend to verify that users are successfully imported.

You would generally be running the above script on regular basis, say each day from `cron(8)` in order to make sure your Zabbix system is in sync with LDAP.
