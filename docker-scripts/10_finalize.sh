#!/bin/bash

chown -R zabbix-ldap-sync:zabbix-ldap-sync /zabbix-ldap-sync
find /zabbix-ldap-sync -type d -exec chmod 755 {} \;
find /zabbix-ldap-sync -type f -exec chmod 644 {} \;

