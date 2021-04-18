#!/bin/bash

set -eux
apt-get install python3-dev libpython3-dev libldap2-dev libsasl2-dev -y
pip3 install -r /requirements.txt
