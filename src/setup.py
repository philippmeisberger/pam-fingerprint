#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'PAM Fingerprint',
    version         = '1.1',
    description     = 'Pluggable Authentication Module for biometric authentication.',
    author          = 'Philipp Meisberger',
    author_email    = 'team@pm-codeworks.de',
    url             = 'http://www.pm-codeworks.de/pamfingerprint.html',
    license         = 'BSD 3 License',
    package_dir     = {'': 'files'},
    packages        = ['pamfingerprint'],
)
