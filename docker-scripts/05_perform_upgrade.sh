#!/bin/bash

set -eux

apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get remove gcc -y
apt-get autoremove -y
rm -rf /var/lib/apt/lists/* /root/.cache
