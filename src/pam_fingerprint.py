#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PAM Fingerprint implementation

Copyright 2014 Philipp Meisberger <team@pm-codeworks.de>,
               Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

import syslog
import hashlib
import os
from configparser import ConfigParser

from pamfingerprint import __version__ as version
from pamfingerprint import CONFIG_FILE
from pyfingerprint.pyfingerprint import PyFingerprint


class UserUnknownException(Exception):
    """Dummy exception class for unknown user."""
    pass


class InvalidUserCredentials(Exception):
    """Dummy exception class for invalid user credentials."""
    pass


def show_pam_text_message(pamh, message, error_message=False):
    """
    Shows a PAM conversation text info.

    :param pamh: The PAM handle
    :param message: The message to print
    :param error_message: True if it is an error or False otherwise
    :return: bool
    """

    try:
        if error_message:
            style = pamh.PAM_ERROR_MSG
        else:
            style = pamh.PAM_TEXT_INFO

        msg = pamh.Message(style, 'PAM Fingerprint {0}: {1}'.format(version, message))
        pamh.conversation(msg)
        return True

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return False


def auth_log(message, priority=syslog.LOG_INFO):
    """
    Sends errors to default authentication log

    :param message: The message to write to syslog
    :param priority: The priority of the syslog message
    """

    syslog.openlog(facility=syslog.LOG_AUTH)
    syslog.syslog(priority, 'PAM Fingerprint: {0}'.format(message))
    syslog.closelog()


def pam_sm_authenticate(pamh, flags, argv):
    """
    PAM service function for user authentication.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    # The authentication service should return [PAM_AUTH_ERROR] if the user has a null authentication token
    flags = pamh.PAM_DISALLOW_NULL_AUTHTOK

    # Initialize authentication progress
    try:
        # Tries to get user which is asking for permission
        username = pamh.ruser

        # Fallback
        if username is None:
            username = pamh.get_user()

        # Be sure the user is set
        if username is None:
            raise UserUnknownException('The user is not known!')

        # Checks if path/file is readable
        if not os.access(CONFIG_FILE, os.R_OK):
            raise Exception('The configuration file "{0}" is not readable!'.format(CONFIG_FILE))

        config_parser = ConfigParser()
        config_parser.read(CONFIG_FILE)

        # Log the user
        auth_log('The user "{0}" is asking for permission for service "{1}".'.format(username, pamh.service),
                 syslog.LOG_DEBUG)

        # Checks if the user was added in configuration
        if not config_parser.has_option('Users', username):
            raise Exception('The user was not added!')

        # Tries to get user information (template position, fingerprint hash)
        user_data = config_parser.get('Users', username).split(',')

        # Validates user information
        if len(user_data) != 2:
            raise InvalidUserCredentials('The user information of "{0}" is invalid!'.format(username))

        expected_position_number = int(user_data[0])
        expected_fingerprint_hash = user_data[1]

    except UserUnknownException as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_USER_UNKNOWN

    except InvalidUserCredentials as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_AUTH_ERR

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_IGNORE

    # Initialize fingerprint sensor
    try:
        # Gets sensor connection values
        port = config_parser.get('PyFingerprint', 'port')
        baud_rate = int(config_parser.get('PyFingerprint', 'baudRate'), 10)
        address = int(config_parser.get('PyFingerprint', 'address'), 16)
        password = int(config_parser.get('PyFingerprint', 'password'), 16)

        # Tries to init PyFingerprint
        fingerprint = PyFingerprint(port, baud_rate, address, password)

        if not fingerprint.verifyPassword():
            raise Exception('The given fingerprint sensor password is wrong!')

    except Exception as e:
        auth_log('The fingerprint sensor could not be initialized: {0}'.format(e), syslog.LOG_ERR)
        show_pam_text_message(pamh, 'Sensor initialization failed!', True)
        return pamh.PAM_IGNORE

    if not show_pam_text_message(pamh, 'Waiting for finger...'):
        return pamh.PAM_CONV_ERR

    # Authentication progress
    try:
        # Tries to read fingerprint
        while not fingerprint.readImage():
            pass

        fingerprint.convertImage(0x01)

        # Gets position of template
        result = fingerprint.searchTemplate()
        position_number = result[0]

        # Checks if the template position is invalid
        if position_number == -1:
            raise Exception('No match found!')

        # Checks if the template position is correct
        if position_number != expected_position_number:
            raise Exception('The template position of the found match is not equal to the stored one!')

        # Gets characteristics
        fingerprint.loadTemplate(position_number, 0x01)
        characteristics = fingerprint.downloadCharacteristics(0x01)

        # Calculates hash of template
        fingerprint_hash = hashlib.sha256(str(characteristics).encode('utf-8')).hexdigest()

        # Checks if the calculated hash is equal to expected hash from user
        if fingerprint_hash == expected_fingerprint_hash:
            auth_log('Access granted!')
            show_pam_text_message(pamh, 'Access granted!')
            return pamh.PAM_SUCCESS
        else:
            auth_log('The found match is not assigned to user!', syslog.LOG_WARNING)
            show_pam_text_message(pamh, 'Access denied!', True)
            return pamh.PAM_AUTH_ERR

    except Exception as e:
        auth_log('Fingerprint read failed: {0}'.format(e), syslog.LOG_CRIT)
        show_pam_text_message(pamh, 'Access denied!', True)
        return pamh.PAM_AUTH_ERR

    # Deny per default
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    """
    PAM service function to alter credentials.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    """
    PAM service function for account management.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    return pamh.PAM_SUCCESS


def pam_sm_open_session(pamh, flags, argv):
    """
    PAM service function to start session.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    """
    PAM service function to terminate session.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    """
    PAM service function for authentication token management.

    :param pamh:
    :param flags:
    :param argv:
    :return: int
    """

    return pamh.PAM_SUCCESS
