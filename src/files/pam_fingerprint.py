#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pamfingerprint
PAM implementation.

Copyright 2015 Philipp Meisberger, Bastian Raschke.
All rights reserved.
"""

import syslog
import hashlib
from pamfingerprint import __version__ as VERSION
from pamfingerprint.Config import Config
from pyfingerprint.pyfingerprint import PyFingerprint


def showPAMTextMessage(pamh, message):
    """
    Shows a PAM conversation text info.

    @param pamh
    @param string message

    @return void
    """

    if ( type(message) != str ):
        raise ValueError('The given parameter is not a string!')

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': '+ message)
    pamh.conversation(msg)


def auth_log(message, priority=syslog.LOG_INFO):
    """
    Sends errors to default authentication log

    @param string message
    @param integer priority
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
    @return integer
    """

    ## Tries to get user which is asking for permission
    try:
        userName = pamh.ruser

        ## Fallback
        if ( userName == None ):
            userName = pamh.get_user()

        ## Be sure the user is set
        if ( userName == None ):
            raise Exception('The user is not known!')

    except Exception as e:
        auth_log(e.message, syslog.LOG_CRIT)
        return pamh.PAM_USER_UNKNOWN

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        auth_log(e.message, syslog.LOG_CRIT)
        return pamh.PAM_IGNORE

    auth_log('The user "' + userName + '" is asking for permission for service "' + str(pamh.service) + '".', syslog.LOG_DEBUG)

    ## Checks if the the user was added in configuration
    if ( config.itemExists('Users', userName) == False ):
        auth_log('The user was not added!', syslog.LOG_ERR)
        return pamh.PAM_IGNORE

    ## Tries to get user information (template position, fingerprint hash)
    try:
        userData = config.readList('Users', userName)

        ## Validates user information
        if ( len(userData) != 2 ):
            raise Exception('The user information of "' + userName + '" is invalid!')

        expectedPositionNumber = int(userData[0])
        expectedFingerprintHash = userData[1]

    except Exception as e:
        auth_log(e.message, syslog.LOG_CRIT)
        return pamh.PAM_AUTH_ERR

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

        if ( fingerprint.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        auth_log('The fingerprint sensor could not be initialized: ' + e.message, syslog.LOG_ERR)
        showPAMTextMessage(pamh, 'Sensor initialization failed!')
        return pamh.PAM_IGNORE

    showPAMTextMessage(pamh, 'Waiting for finger...')

    ## Tries to read fingerprint
    try:
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
            showPAMTextMessage(pamh, 'Access denied!')
            return pamh.PAM_AUTH_ERR

    except Exception as e:
        auth_log('Fingerprint read failed: ' + e.message, syslog.LOG_CRIT)
        showPAMTextMessage(pamh, 'Access denied!')
        return pamh.PAM_AUTH_ERR

    ## Denies for default
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
    """
    PAM service function to alter credentials.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS


def pam_sm_acct_mgmt(pamh, flags, argv):
    """
    PAM service function for account management.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS


def pam_sm_open_session(pamh, flags, argv):
    """
    PAM service function to start session.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS


def pam_sm_close_session(pamh, flags, argv):
    """
    PAM service function to terminate session.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS


def pam_sm_chauthtok(pamh, flags, argv):
    """
    PAM service function for authentication token management.

    @param pamh
    @param flags
    @param argv
    @return integer
    """

    return pamh.PAM_SUCCESS
