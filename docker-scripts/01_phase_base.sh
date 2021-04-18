#!/bin/bash

set -eux

apt-get autoremove -y

apt-get update 
apt-get install vim-tiny python3 python3-pip less -y
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get autoremove -y
apt-get clean
apt-get autoremove -y

groupadd -g 1001 zabbix-ldap-sync
useradd -g zabbix-ldap-sync -G zabbix-ldap-sync -u 1001 -m -s /bin/bash zabbix-ldap-sync

chown -R zabbix-ldap-sync:zabbix-ldap-sync /home/zabbix-ldap-sync

echo "set nocompatible" > /home/zabbix-ldap-sync/.vimrc

