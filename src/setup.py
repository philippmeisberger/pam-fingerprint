#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PAM Fingerprint

Copyright 2014 Philipp Meisberger <team@pm-codeworks.de>,
               Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

from setuptools import setup

import sys
sys.path.insert(0, './files/')

import pamfingerprint

setup(
    name            = 'libpam-fingerprint',
    version         = pamfingerprint.__version__,
    description     = 'Linux Pluggable Authentication Module (PAM) for fingerprint authentication',
    author          = 'Philipp Meisberger',
    author_email    = 'team@pm-codeworks.de',
    url             = 'http://www.pm-codeworks.de/pamfingerprint.html',
    license         = 'D-FSL',
    package_dir     = {'': 'files'},
    packages        = ['pamfingerprint'],
)
