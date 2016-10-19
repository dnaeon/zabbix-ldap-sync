#
# spec file for package zabbix-ldap-sync
#
# Copyright (c) 2016 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           zabbix-ldap-sync
Version:        0.1
Release:        1
Url:            https://github.com/dnaeon/zabbix-ldap-sync
Summary:        Sync your Zabbix users with LDAP directory server
License:        BSD
Group:          Productivity
Source:         https://github.com/dnaeon/zabbix-ldap-sync/archive/master.zip
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Requires:       python-ldap
Requires:       pyzabbix >= 0.7.4
Requires:       docopt >= 0.6.2

%description
The zabbix-ldap-sync script is used for keeping your Zabbix users in 
sync with an LDAP directory server.

It can automatically import existing LDAP groups and users into Zabbix,
thus making it easy for you to keep your Zabbix users in sync with LDAP.

Tested against Zabbix 3.0.

%prep
%setup -q -n zabbix-ldap-sync-%{version}

%install
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}

cp %{name} %{buildroot}%{_datadir}/usr/sbin
cp zabbix-ldap.conf %{buildroot}%{_sysconfdir}/%{name}/

%files
%defattr(-,root,root,-)
%doc README.md
%config %{_sysconfdir}/%{name}/zabbix-ldap.conf
%{_sbindir}/%{name}

%changelog
* Tue Oct 19 2016 Benoit Mortier <benoit.mortier@opensides.be> - 0.1-1
- First release



