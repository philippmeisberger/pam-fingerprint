"""
"" pamfingerprint
"" PAM implementation.
""
"" Copyright 2014 Philipp Meisberger, Bastian Raschke.
"" All rights reserved. 
"""

import sys 
sys.path.append('/usr/lib')

from pamfingerprint.version import VERSION
from pamfingerprint.Config import *

from PyFingerprint.PyFingerprint import *

import logging

## Configures logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

## Creates and adds a file handler to logger
fileHandler = logging.FileHandler('/var/log/pamfingerprint.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(fileHandler)


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
            user = str(pamh.get_user())
        else:
            user = str(pamh.ruser)

    except pamh.exception, e:
        logger.error(e.message, exc_info=True)
        return pamh.PAM_USER_UNKNOWN

    ## Be sure the user is set 
    if ( user == None ):
        logger.error('The user is not known!')
        return pamh.PAM_USER_UNKNOWN
  
    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception, e:
        logger.error(e.message, exc_info=True)
        return pamh.PAM_IGNORE

    logger.info('The user "' + user + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## TODO: Change to fingerprint hash
    ## Checks if the user is assigned to any ID
    try:
        expectedId = config.readInteger('Users', user)

    except ConfigParser.NoOptionError:
        logger.error('The user "' + user + '" is not assigned!', exc_info=False)
        return pamh.PA_AUTH_ERR

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')
    
    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

    except Exception, e:
        logger.error('Connection to fingerprint sensor failed!', exc_info=True)
        msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': ' + e.message)
        pamh.conversation(msg)
        return pamh.PAM_IGNORE

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...')
    pamh.conversation(msg)

    ## Tries to read fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception, e:
        logger.error(e.message, exc_info=True)
        return pamh.PAM_ABORT

    ## Checks if user ID matches template ID
    if ( ( result[0] == True ) and ( expectedId == result[1] ) ):
        logger.info('Access granted!')
        msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access granted!')
        pamh.conversation(msg)
        return pamh.PAM_SUCCESS
    else:
        logger.info('No match found or the found match is not assigned to user!')
        msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!')
        pamh.conversation(msg)
        return pamh.PA_AUTH_ERR

    ## Denies for default
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
