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

    print 'pamfingerprint ' + VERSION

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PAM_IGNORE

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pamfingerprint.log', logLevel)

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PAM_IGNORE

    logger.log(Logger.NOTICE, 'The user "' + str(pamh.ruser) + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## Checks if the user is assigned to any ID
    try:
        expectedId = config.readInteger('Users', pamh.ruser)

    except ConfigParser.NoOptionError:
        logger.log(Logger.NOTICE, 'The user "' + str(pamh.ruser) + '" is not assigned!')
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
        logger.log(Logger.ERROR, 'Exception: ' + str(e))
        return pamh.PAM_IGNORE

    ## Tries to read fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception as e:
        logger.log(Logger.ERROR, 'Exception: ' + str(e))
        return pamh.PAM_IGNORE

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