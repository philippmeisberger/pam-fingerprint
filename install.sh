#!/bin/sh

find ./src/ -type f -name *.pyc -exec rm {} \;

cp ./src/etc/pamfingerprint.conf /etc/

cp ./src/lib/security/pam_fingerprint.py /lib/security/
cp -r ./src/usr/* /usr/

cp ./src/var/log/pamfingerprint.log /var/log/
chown 1000:1000 /var/log/pamfingerprint.log