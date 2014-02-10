#!/bin/sh

find ./src/ -type f -name *.pyc -exec rm {} \;

cp -r ./src/etc/* /etc/
chmod 644 /etc/pamfingerprint.conf

cp ./src/lib/security/pam_fingerprint.py /lib/security/
#cp -r ./src/usr/* /usr/
cp -r ./src/usr/lib/pamfingerprint /usr/lib/
#chmod 700 /usr/bin/pamfingerprint-conf

cp ./src/var/log/pamfingerprint.log /var/log/
#chmod 1000:1000 /var/log/pamfingerprint.log
