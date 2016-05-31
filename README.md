PAM Fingerprint
===============

PAM Fingerprint is a Linux Pluggable Authentication Module (PAM) for fingerprint authentication. It uses the ZhianTec ZFM-20 fingerprint sensor (known as "Arduino fingerprint sensor") in conjunction with the PyFingerprint library <https://github.com/bastianraschke/pyfingerprint>.

Installation
------------

Add PM Codeworks repository

    ~# wget http://apt.pm-codeworks.de/pm-codeworks.list -P /etc/apt/sources.d/

Add PM Codeworks key

    ~# wget -O - http://apt.pm-codeworks.de/pm-codeworks.de.gpg.key | apt-key add -
    ~# apt-get update

Install the packages

    ~# apt-get install python-fingerprint libpam-fingerprint

Add group "dialout" for each user which should be able to use pamfingerprint

    ~# usermod -a -G dialout <username>
    ~# reboot

Setup
-----

Enable PAM Fingerprint for a user

    ~# pamfingerprint-conf --add-user <username>

Test if everything works well

    ~# pamfingerprint-check --check-user <username>

Questions and suggestions
-------------------------

If you have any questions to this project just ask me via email:

<team@pm-codeworks.de>