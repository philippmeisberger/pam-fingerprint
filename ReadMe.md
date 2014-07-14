Install instructions for Debian 7
=================================

* Add PM Codeworks repository:
    * `~# wget http://apt.pm-codeworks.de/pm-codeworks.list -P /etc/apt/sources.d/`

* Add PM Codeworks key:
    * `~# wget -O - http://apt.pm-codeworks.de/pm-codeworks.de.gpg.key | apt-key add -`
    * `~# apt-get update`

* Install the package:
    * `~# apt-get install pamfingerprint`

* Install "PyFingerprint":
    * `~# wget -O - https://sicherheitskritisch.de/PyFingerprint.tar.gz | tar xvzf - -C /`

* Add group "dialout" for each user which should be able to use pamfingerprint:
    * `~# usermod -a -G dialout <username>`
    * `~# reboot`

* Setup user
    * `~# pamfingerprint-conf --add-user <username>`
