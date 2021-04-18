FROM ubuntu:latest

MAINTAINER operations@flipapp.de

USER 0
ADD /docker-scripts /tmp/setup
RUN chmod 755 /tmp/setup/*.sh
RUN /tmp/setup/01_phase_base.sh
ADD /requirements.txt /requirements.txt
RUN /tmp/setup/04_install.sh
ARG FORCE_UPGRADE_MARKER=unknown
RUN /tmp/setup/05_perform_upgrade.sh
ADD /lib /zabbix-ldap-sync/lib
ADD /zabbix-ldap-sync /zabbix-ldap-sync/lib
RUN /tmp/setup/10_finalize.sh
USER 1001

WORKDIR /
ENTRYPOINT ["python3", "/zabbix/__main__.py"]
