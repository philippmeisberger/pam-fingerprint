#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PAM Fingerprint

Copyright 2014 Philipp Meisberger <team@pm-codeworks.de>,
               Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

from setuptools import setup
from src.pamfingerprint import __version__

setup(
    name='libpam-fingerprint',
    version=__version__,
    description='Linux Pluggable Authentication Module (PAM) for fingerprint authentication',
    author='Philipp Meisberger',
    author_email='team@pm-codeworks.de',
    url='https://www.pm-codeworks.de/pamfingerprint.html',
    license='AGPL',
    package_dir={'': 'src'},
    packages=['pamfingerprint'],
    install_requires=['pyfingerprint'],
    classifiers=[
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
    ]
)
