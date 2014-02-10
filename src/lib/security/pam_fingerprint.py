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

"""
"" PAM service function for user authentication.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_authenticate(pamh, flags, argv):

    ## Tries to get user which is asking for permission
    try:
        if ( pamh.ruser == None ):
            user = pamh.get_user()
        else:
            user = pamh.ruser

    except pamh.exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e))
        pamh.conversation(msg)
        return pamh.PAM_USER_UNKNOWN

    ## Be sure the user is set 
    if ( user == None ):
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'The user is not known!')
        pamh.conversation(msg)
        return pamh.PAM_USER_UNKNOWN
  
    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e))
        pamh.conversation(msg)
        return pamh.PAM_IGNORE

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pamfingerprint.log', logLevel, pamh)

    except Exception as e:
        msg = pamh.Message(pamh.PAM_ERROR_MSG, 'Exception: ' + str(e))
        pamh.conversation(msg)
        return pamh.PAM_IGNORE

    logger.log(Logger.NOTICE, 'The user "' + str(user) + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## Checks if the user is assigned to any ID
    try:
        expectedId = config.readInteger('Users', user)

    except ConfigParser.NoOptionError:
        logger.log(Logger.NOTICE, 'The user "' + str(user) + '" is not assigned!')
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

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...')
    pamh.conversation(msg)

    ## Tries to read fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception as e:
        logger.log(Logger.ERROR, 'Exception:' + str(e))
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
