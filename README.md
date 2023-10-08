PAM Fingerprint
===============

PAM Fingerprint is a Linux Pluggable Authentication Module (PAM) for password-less fingerprint authentication. It uses the ZhianTec ZFM-20 fingerprint sensor (known as "Arduino fingerprint sensor") in conjunction with the PyFingerprint library <https://github.com/bastianraschke/pyfingerprint>.

Per default the password authentication is set as fallback in case no fingerprint sensor is connected. Two-factor authentication is also possible. The module has to be configured by the `pamfingerprint-conf` program.

Installation
------------

There are two ways of installing PAM Fingerprint: Installation of the stable or latest version. The stable version is distributed through the PM Code Works APT repository and is fully tested but does not contain the latest changes.

### Installation of the stable version

Add PM Code Works repository

Debian 12:

    ~# echo "deb https://apt.pm-codeworks.de bookworm main" | tee /etc/apt/sources.list.d/pm-codeworks.list

Add PM Code Works signing key

    ~# wget -qO - https://apt.pm-codeworks.de/pm-codeworks.de.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/pm-codeworks.de.gpg
    ~# apt update

Install the packages

    ~# apt install python-fingerprint libpam-fingerprint

### Installation of the latest version

The latest version contains the latest changes that may not have been fully tested and should therefore not be used in production. It is recommended to install the stable version.

Install required packages for building

    ~# apt install git devscripts equivs

Clone this repository

    ~$ git clone https://github.com/philippmeisberger/pam-fingerprint.git

Build the package

    ~$ cd ./pam-fingerprint/
    ~$ sudo mk-build-deps -i debian/control
    ~$ dpkg-buildpackage -uc -us

Install the package

    ~# dpkg -i ../libpam-fingerprint*.deb

Install missing dependencies

    ~# apt install -f

Setup
-----

Add group "dialout" for each user which should be able to use PAM Fingerprint

    ~# usermod -a -G dialout <username>
    ~# reboot

Enable PAM Fingerprint for a user

    ~# pamfingerprint-conf --add-user <username>

Test if everything works well

    ~# pamfingerprint-conf --check-user <username>

Questions and suggestions
-------------------------

If you have any questions to this project just ask me via email:

<team@pm-codeworks.de>
