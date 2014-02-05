#!/bin/sh

find . -type f -name *.pyc -exec rm {} \;

cp etc/pamfingerprint.conf /etc/

cp lib/security/pam_fingerprint.py /lib/security/
cp -r usr/* /usr/

cp var/log/pamfingerprint.log /var/log/