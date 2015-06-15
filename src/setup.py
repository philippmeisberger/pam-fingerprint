#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name            = 'PAM Fingerprint',
    version         = '1.2',
    description     = 'Pluggable Authentication Module for biometric authentication.',
    author          = 'Philipp Meisberger',
    author_email    = 'team@pm-codeworks.de',
    url             = 'http://www.pm-codeworks.de/pamfingerprint.html',
    license         = 'D-FSL',
    package_dir     = {'': 'files'},
    packages        = ['pamfingerprint'],
)
