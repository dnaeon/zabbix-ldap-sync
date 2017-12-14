## LOOKING FOR MAINTAINERS

I no longer have enough time to actively work on this project, therefore I'm looking for
maintainers that can step up and take ownership of this project.

If you'd like to become maintainer of this project, please contact me.

## zabbix-ldap-sync -- Sync your Zabbix users with LDAP directory server

The *zabbix-ldap-sync* script is used for keeping your Zabbix users in sync with an LDAP directory server.

It can automatically import existing LDAP groups and users into Zabbix, thus making it easy for you to keep your Zabbix users in sync with LDAP.

## Requirements

* Python 3.x.x
* [pyldap](https://pypi.python.org/pypi/pyldap/)
* [pyzabbix](https://github.com/lukecyca/pyzabbix)
* [docopt](https://github.com/docopt/docopt)
* Zabbix 3.4

You also need to have your Zabbix Frontend configured to authenticate against an AD/LDAP directory server.
(using http or ldap-auth)

Check the official documentation of Zabbix on how to 
[configure Zabbix to authenticate against an AD/LDAP directory server](https://www.zabbix.com/documentation/2.2/manual/web_interface/frontend_sections/administration/authentication).

### Setup virtualenv

```
apt-get install python-dev virtualenv libpython3.6-dev libldap2-dev libsasl2-dev
virtualenv -p python3 env
source env/bin/activate
pip install pyldap
pip install pyzabbix
pip install docopt
```

## Configuration

In order to use the *zabbix-ldap-sync* script we need to create a configuration file describing the various LDAP and Zabbix related config entries.

### Config file sections

#### [ldap]
* `type` - Select type of ldap server, can be `activedirectory` or `openldap`
* `uri` - URI of the LDAP server, including port
* `base` - Base `Distinguished Name`
* `binduser` - LDAP user which has permissions to perform LDAP search
* `bindpass` - Password for LDAP user
* `groups` - LDAP groups to sync with Zabbix (support wildcard - TESTED ONLY with Active Directory, see Command-line arguments)
* `media` - Name of the LDAP attribute of user object, that will be used to set `Send to` property of Zabbix user media. This entry is optional, default value is `mail`.

[ad]
* `filtergroup` = The ldap filter to get group in ActiveDirectory mode, by default `(&(objectClass=group)(name=%s))`
* `filteruser` = The ldap filter to get the users in ActiveDirectory mode, by default `(objectClass=user)(objectCategory=Person)`
* `filterdisabled` = The filter to get the disabled user in ActiveDirectory mode, by default `(!(userAccountControl:1.2.840.113556.1.4.803:=2))`
* `filtermemberof` = The filter to get memberof in ActiveDirectory mode, by default `(memberOf:1.2.840.113556.1.4.1941:=%s)`
* `groupattribute` = The attribute used for membership in a group in ActiveDirectory mode, by default `member`
* `userattribute` = The attribute for users in ActiveDirectory mode `sAMAccountName`

[openldap]
* `type` = The storage mode for group and users can be `posix` or `groupofnames` 
* `filtergroup` = The ldap filter to get group in OpenLDAP mode, by default `(&(objectClass=posixGroup)(cn=%s))`
* `filteruser` = The ldap filter to get the users in OpenLDAP mode, by default `(&(objectClass=posixAccount)(uid=%s))`
* `groupattribute` = The attribute used for membership in a group in OpenLDAP mode, by default `memberUid`
* `userattribute` = The attribute for users in openldap mode, by default `uid`

#### [zabbix]
* `server` - Zabbix URL
* `username` - Zabbix username. This user must have permissions to add/remove users and groups. Typically, this would be `Zabbix Admin` account.
* `password` - Password for Zabbix user
* `auth` - can be `http` (for basic auth) or `webform` (for regular form based login)

#### [user]
Allows to override various properties for Zabbix users created by script. See [User object](https://www.zabbix.com/documentation/3.2/manual/api/reference/user/object) in Zabbix API documentation for available properties. If section/property doesn't exist, defaults are:

 * `type = 1` - User type. Possible values: `1` - (default) Zabbix user; `2` - Zabbix admin; `3` - Zabbix super admin. 

#### [media]
Allows to override media type and various properties for Zabbix media for users created by script.

* `decription` - Description of Zabbix media (`Email`, `Jabber`, `SMS`, etc...). This entry is optional, default value is `Email`.

You can configure additional properties in this section. See [Media object](https://www.zabbix.com/documentation/3.2/manual/api/reference/usermedia/object#media) in Zabbix API documentation for available properties. If this section/property doesn't exist, defaults fro additional properties are:

* `active = 0` - Whether the media is enabled. Possible values: `0`- enabled; `1` - disabled.
* `period = 1-7,00:00-24:00` - Time when the notifications can be sent as a [time period](https://www.zabbix.com/documentation/3.2/manual/appendix/time_period).
* `severity = 63` - Decimal value of trigger severities to send notifications about. Each severity value occupies a position of a 6-bit value. Use this table to calculate decimal representation:

```
╔═════════════╦════════╦════╦═══════╦═══════╦═══════════╦══════════════╗
║  Severity   ║Disaster║High║Average║Warning║Information║Not Classified║
╠═════════════╬════════╬════╬═══════╬═══════╬═══════════╬══════════════╣
║  Enabled ?  ║      1 ║  1 ║     1 ║     1 ║         1 ║            1 ║
╠═════════════╬════════╩════╩═══════╩═══════╩═══════════╩══════════════╣
║Decimal value║                     111111 = 63                        ║
║             ║           Linux: printf '%x\n' "$((2#111000))"         ║
╚═════════════╩════════════════════════════════════════════════════════╝
```


## Configuration file example

    [ldap]
    type = activedirectory
    uri = ldaps://ldap.example.org:389/
    base = dc=example,dc=org
    binduser = DOMAIN\ldapuser
    bindpass = ldappass
    groups = sysadmins
    media = mail

    [ad]
    filtergroup = (&(objectClass=group)(name=%s))
    filteruser = (objectClass=user)(objectCategory=Person)
    filterdisabled = (!(userAccountControl:1.2.840.113556.1.4.803:=2))
    filtermemberof = (memberOf:1.2.840.113556.1.4.1941:=%s)
    groupattribute = member
    userattribute = sAMAccountName

    [openldap]
    type = posix
    filtergroup = (&(objectClass=posixGroup)(cn=%s))
    filteruser = (&(objectClass=posixAccount)(uid=%s))
    groupattribute = memberUid
    userattribute = uid
    
    [zabbix]
    server = http://zabbix.example.org/zabbix/
    username = admin
    password = adminp4ssw0rd
    
    [user]
    type = 3
    url = http://zabbix.example.org/zabbix/hostinventories.php
    autologin = 1
    
    [media]
    description = Email
    active = 0
    period = 1-5,07:00-22:00
    severity = 63

## Command-line arguments

    Usage: zabbix-ldap-sync [-lsrwdn] [--verbose] -f <config>
       zabbix-ldap-sync -v
       zabbix-ldap-sync -h

    Options:
      -h, --help                    Display this usage info
      -v, --version                 Display version and exit
      -l, --lowercase               Create AD user names as lowercase
      -s, --skip-disabled           Skip disabled AD users
      -r, --recursive               Resolves AD group members recursively (i.e. nested groups)
      -w, --wildcard-search         Search AD group with wildcard (e.g. R.*.Zabbix.*) - TESTED ONLY with Active Directory
      -d, --delete-orphans          Delete Zabbix users that don't exist in a LDAP group
      -n, --no-check-certificate    Don't check Zabbix server certificate
      --verbose                     Print debug message from ZabbixAPI
      -f <config>, --file <config>  Configuration file to use

## Importing LDAP users into Zabbix

Now that we have the above mentioned configuration file created, let's import our groups and users from LDAP to Zabbix.

	$ zabbix-ldap-sync -f /path/to/zabbix-ldap.conf
	
Once the script completes, check your Zabbix Frontend to verify that users are successfully imported.

To sync different LDAP groups with different options, create separate config file for each group and run `zabbix-ldap-sync`:

	$ zabbix-ldap-sync -f /path/to/zabbix-ldap-admins.conf
	$ zabbix-ldap-sync -f /path/to/zabbix-ldap-users.conf

You would generally be running the above scripts on regular basis, say each day from `cron(8)` in order to make sure your Zabbix system is in sync with LDAP.
