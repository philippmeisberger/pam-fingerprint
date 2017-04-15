PAM Fingerprint
===============

PAM Fingerprint is a Linux Pluggable Authentication Module (PAM) for password-less fingerprint authentication. It uses the ZhianTec ZFM-20 fingerprint sensor (known as "Arduino fingerprint sensor") in conjunction with the PyFingerprint library <https://github.com/bastianraschke/pyfingerprint>.

Per default the password authentication is set as fallback in case no fingerprint sensor is connected. Two-factor authentication is also possible. The module has to be configured by the `pamfingerprint-conf` program. To simulate an authentication process the `pamfingerprint-check` program can be used.

Installation
------------

Add PM Codeworks repository

    ~# wget http://apt.pm-codeworks.de/pm-codeworks.list -P /etc/apt/sources.d/

Add PM Codeworks key

    ~# wget -O - http://apt.pm-codeworks.de/pm-codeworks.de.gpg | apt-key add -
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
