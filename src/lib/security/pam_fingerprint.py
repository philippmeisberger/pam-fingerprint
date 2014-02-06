"""
"" PAM Fingerprint
"" PAM module implementation.
""
"" Copyright 2014 Philipp Meisberger, Bastian Raschke.
"" All rights reserved. 
"""

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

    print 'pamfingerprint: User "' + str(pamh.ruser) + '" is asking for permission for service "' + str(pamh.service) + '".'

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

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

    except Exception as e:
        print 'PyFingerprint exception: ' + str(e)
        return pamh.PAM_IGNORE

    ## Tries to read fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception as e:
        print 'PyFingerprint exception: ' + str(e)
        return pamh.PAM_IGNORE
        return pamh.PAM_IGNORE

    if ( result[0] == False ):
        print 'No match found!'
        return pamh.PA_AUTH_ERR

    positionNumber = result[1]

    try:
        assignedPositionNumber = config.readInteger('Users', pamh.ruser)

    except ConfigParser.NoOptionError:
        print 'The found match is not assigned to any user!'
        return pamh.PA_AUTH_ERR

    ## Checks if the position number of fingerprint template is assigned to user
    if ( assignedPositionNumber == positionNumber ):
        print 'Access granted.'
        return pamh.PAM_SUCCESS
    else:
        print 'The found match is not assigned to user!'
        return pamh.PA_AUTH_ERR

    ## Denies for default
    print 'Access denied!'
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

    ## Needed for getting root access rights!
    return pamh.PAM_SUCCESS
