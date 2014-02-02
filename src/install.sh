#!/bin/sh

cp etc/pam_fingerprint.conf /etc/

## TODO
## chmod 600 /etc/pam_fingerprint.conf

cp lib/security/pam_fingerprint.py /lib/security/
# TODO: better ln -s usr/bin/pam_fingerprint-conf /usr/bin/pamfingerprint-conf
cp usr/bin/pamfingerprint-conf /usr/bin/
cp -r usr/lib/* /usr/lib/

cp var/log/pam_fingerprint.log /var/log/

## TODO
chown 1000:1000 /var/log/pam_fingerprint.log