#
# spec file for package zabbix-ldap-sync
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
Requires:       python-pyzabbix >= 0.7.4
Requires:       python-docopt >= 0.6.2

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

cp %{name} %{buildroot}%{_sbindir}
cp zabbix-ldap.conf %{buildroot}%{_sysconfdir}/%{name}/

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%config %{_sysconfdir}/%{name}/zabbix-ldap.conf
%{_sbindir}/%{name}

%changelog
* Tue Oct 19 2016 Benoit Mortier <benoit.mortier@opensides.be> - 0.1-1
- First release



