PAM Fingerprint
===============


PAM Fingerprint is a open-source Unix PAM module that allows biometric fingerprint
authentification.

It is totally written in python and uses a python framework called
pam_python as adapter to implement the PAM interface that is written in C.
PAM Fingerprint uses the Adafruit optical fingerprint sensor (http://www.adafruit.com/products/751) for biometric authentification. Pyserial, a python written library for serial connections, is used for the connection between the sensor and a computer. The sensor is connected with a USB TTL converter.


Requirements:

~# apt-get install python
~# apt-get install python-pip
~# pip install pyserial

~# apt-get install pam_python
