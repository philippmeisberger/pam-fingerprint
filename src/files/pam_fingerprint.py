#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PAM Fingerprint implementation

Copyright 2014 Philipp Meisberger <team@pm-codeworks.de>,
               Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

import syslog
import hashlib

from pamfingerprint import __version__ as VERSION
from pamfingerprint.Config import Config
from pyfingerprint.pyfingerprint import PyFingerprint

class UserUnknownException(Exception):
    """
    Dummy exception class for unknown user.

    """

    pass

class InvalidUserCredentials(Exception):
    """
    Dummy exception class for invalid user credentials.

    """

    pass

def showPAMTextMessage(pamh, message, errorMessage=False):
    """
    Shows a PAM conversation text info.

    @param pamh
    The PAM handle.

    @param str message
    The message to print.

    @return bool
    """

    try:
        if ( errorMessage == True ):
            style = pamh.PAM_ERROR_MSG
        else:
            style = pamh.PAM_TEXT_INFO

        msg = pamh.Message(style, 'pamfingerprint ' + VERSION + ': '+ str(message))
        pamh.conversation(msg)
        return True

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return False


def auth_log(message, priority=syslog.LOG_INFO):
    """
    Sends errors to default authentication log

    @param str message
    The message to write to syslog.

    @param int priority
    The priority of the syslog message.

    @return void
    """

    syslog.openlog(facility=syslog.LOG_AUTH)
    syslog.syslog(priority, 'pamfingerprint: ' + message)
    syslog.closelog()


def pam_sm_authenticate(pamh, flags, argv):
    """
    PAM service function for user authentication.

    @param pamh
    @param flags
    @param argv

    @return int
    """

    ## The authentication service should return [PAM_AUTH_ERROR] if the user has a null authentication token
    flags = pamh.PAM_DISALLOW_NULL_AUTHTOK

    ## Initialize authentication progress
    try:
        ## Tries to get user which is asking for permission
        userName = pamh.ruser

        ## Fallback
        if ( userName == None ):
            userName = pamh.get_user()

        ## Be sure the user is set
        if ( userName == None ):
            raise UserUnknownException('The user is not known!')

        ## Tries to init config file
        config = Config('/etc/pamfingerprint.conf')

        auth_log('The user "' + userName + '" is asking for permission for service "' + str(pamh.service) + '".', syslog.LOG_DEBUG)

        ## Checks if the the user was added in configuration
        if ( config.itemExists('Users', userName) == False ):
            raise Exception('The user was not added!')

        ## Tries to get user information (template position, fingerprint hash)
        userData = config.readList('Users', userName)

        ## Validates user information
        if ( len(userData) != 2 ):
            raise InvalidUserCredentials('The user information of "' + userName + '" is invalid!')

        expectedPositionNumber = int(userData[0])
        expectedFingerprintHash = userData[1]

    except UserUnknownException as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_USER_UNKNOWN

    except InvalidUserCredentials as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_AUTH_ERR

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_IGNORE

    ## Initialize fingerprint sensor
    try:
        ## Gets sensor connection values
        port = config.readString('PyFingerprint', 'port')
        baudRate = config.readInteger('PyFingerprint', 'baudRate')
        address = config.readHex('PyFingerprint', 'address')
        password = config.readHex('PyFingerprint', 'password')

        ## Tries to init PyFingerprint
        fingerprint = PyFingerprint(port, baudRate, address, password)

        if ( fingerprint.verifyPassword() == False ):
            raise Exception('The given fingerprint sensor password is wrong!')

    except Exception as e:
        auth_log('The fingerprint sensor could not be initialized: ' + str(e), syslog.LOG_ERR)
        showPAMTextMessage(pamh, 'Sensor initialization failed!', True)
        return pamh.PAM_IGNORE

    if ( showPAMTextMessage(pamh, 'Waiting for finger...') == False ):
        return pamh.PAM_CONV_ERR

    ## Authentication progress
    try:
        ## Tries to read fingerprint
        while ( fingerprint.readImage() == False ):
            pass

        fingerprint.convertImage(0x01)

        ## Gets position of template
        result = fingerprint.searchTemplate()
        positionNumber = result[0]

        ## Checks if the template position is invalid
        if ( positionNumber == -1 ):
            raise Exception('No match found!')

        ## Checks if the template position is correct
        if ( positionNumber != expectedPositionNumber ):
            raise Exception('The template position of the found match is not equal to the stored one!')

        ## Gets characteristics
        fingerprint.loadTemplate(positionNumber, 0x01)
        characterics = fingerprint.downloadCharacteristics(0x01)

        ## Calculates hash of template
        fingerprintHash = hashlib.sha256(str(characterics)).hexdigest()

        ## Checks if the calculated hash is equal to expected hash from user
        if ( fingerprintHash == expectedFingerprintHash ):
            auth_log('Access granted!')
            showPAMTextMessage(pamh, 'Access granted!')
            return pamh.PAM_SUCCESS
        else:
            auth_log('The found match is not assigned to user!', syslog.LOG_WARNING)
            showPAMTextMessage(pamh, 'Access denied!', True)
            return pamh.PAM_AUTH_ERR

    except Exception as e:
        auth_log('Fingerprint read failed: ' + str(e), syslog.LOG_CRIT)
        showPAMTextMessage(pamh, 'Access denied!', True)
        return pamh.PAM_AUTH_ERR

    ## Denies for default
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    """
    PAM service function to alter credentials.

    @param pamh
    @param flags
    @param argv
    @return int
    """

    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    """
    PAM service function for account management.

    @param pamh
    @param flags
    @param argv
    @return int
    """

    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
    """
    PAM service function to start session.

    @param pamh
    @param flags
    @param argv
    @return int
    """

    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
    """
    PAM service function to terminate session.

    @param pamh
    @param flags
    @param argv
    @return int
    """

    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
    """
    PAM service function for authentication token management.

    @param pamh
    @param flags
    @param argv
    @return int
    """

    return pamh.PAM_SUCCESS
