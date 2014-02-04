#!/bin/sh

cp etc/pamfingerprint.conf /etc/

## TODO
## chmod 600 /etc/pamfingerprint.conf

cp lib/security/pam_fingerprint.py /lib/security/
# TODO: better ln -s usr/bin/pam_fingerprint-conf /usr/bin/pamfingerprint-conf
cp usr/bin/pamfingerprint-conf /usr/bin/
cp -r usr/lib/* /usr/lib/

cp var/log/pamfingerprint.log /var/log/

## TODO
chown 1000:1000 /var/log/pamfingerprint.log