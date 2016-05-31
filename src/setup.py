#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PAM Fingerprint

Copyright 2014 Philipp Meisberger <team@pm-codeworks.de>,
               Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

from setuptools import setup, find_packages

import sys
sys.path.append('./files/')

## Dynamically get the module version
packageVersion = __import__('pamfingerprint').__version__

setup(
    name            = 'PAM Fingerprint',
    version         = packageVersion,
    description     = 'Linux Pluggable Authentication Module (PAM) for fingerprint authentication',
    author          = 'Philipp Meisberger',
    author_email    = 'team@pm-codeworks.de',
    url             = 'http://www.pm-codeworks.de/pamfingerprint.html',
    license         = 'D-FSL',
    package_dir     = {'': 'files'},
    packages        = ['pamfingerprint'],
)
