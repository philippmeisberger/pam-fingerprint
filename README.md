PAM Fingerprint
===============

PAM Fingerprint is a Linux Pluggable Authentication Module (PAM) for fingerprint authentication. The ZhianTec ZFM-20 fingerprint sensor (known as "Arduino fingerprint sensor") is required.

Installation
------------

Add PM Codeworks repository

    ~# wget http://apt.pm-codeworks.de/pm-codeworks.list -P /etc/apt/sources.d/

Add PM Codeworks key

    ~# wget -O - http://apt.pm-codeworks.de/pm-codeworks.de.gpg.key | apt-key add -
    ~# apt-get update

Install the package

    ~# apt-get install libpam-fingerprint

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