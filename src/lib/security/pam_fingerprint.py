"""
"" PAM Fingerprint
"" PAM module implementation.
""
"" Copyright 2014 Philipp Meisberger, Bastian Raschke.
"" All rights reserved. 
"""

import sys 
sys.path.append('/usr/lib')

from pamfingerprint.version import VERSION
from pamfingerprint.classes.Logger import *
from pamfingerprint.classes.Config import *

from PyFingerprint.PyFingerprint import *

import os

"""
"" PAM service function for user authentication.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_authenticate(pamh, flags, argv):

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...\n')
    pamh.conversation(msg)

    try:
        if ( pamh.ruser == None ):
            user = pamh.get_user()
        else:
            user = pamh.ruser

    except pamh.exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e) +'\n')
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e) +'\n')
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pamfingerprint.log', logLevel)

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e) +'\n')
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    logger.log(Logger.NOTICE, 'User "' + str(user) + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## Checks if the user is assigned to any ID
    try:
        expectedId = config.readInteger('Users', user)

    except ConfigParser.NoOptionError:
        logger.log(Logger.NOTICE, 'User "' + str(user) + '" is not assigned!')
        return pamh.PA_AUTH_ERR

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e) +'\n')
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    ## Tries to read fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e) +'\n')
        pamh.conversation(msg)
        return pamh.PAM_ABORT

    if ( result[0] == False ):
        logger.log(Logger.NOTICE, 'No match found!')
        return pamh.PA_AUTH_ERR

    positionNumber = result[1]

    ## Checks if user ID matches template ID
    if ( expectedId == positionNumber ):
        logger.log(Logger.NOTICE, 'Access granted.')
        return pamh.PAM_SUCCESS
    else:
        logger.log(Logger.WARNING, 'The found match is not assigned to user!')
        return pamh.PA_AUTH_ERR

    ## Denies for default
    logger.log(Logger.NOTICE, 'Access denied!')
    return pamh.PA_AUTH_ERR

"""
"" PAM service function to alter credentials.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_setcred(pamh, flags, argv):

    return pamh.PAM_SUCCESS
