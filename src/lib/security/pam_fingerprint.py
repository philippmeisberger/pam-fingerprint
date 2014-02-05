"""
"" PAM Fingerprint
"" PAM interface implementation
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
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

    print 'pamfingerprint: loading module for user "' + str(pamh.ruser) + '" [service "' + str(pamh.service) + '"].'

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PA_AUTH_ERR

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pamfingerprint.log', logLevel)

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PA_AUTH_ERR

    ## Gets connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PA_AUTH_ERR

    ## Tries to check fingerprint
    try:
        result = fingerprint.searchTemplate()

    except Exception as e:
        print 'Exception: ' + str(e)
        return pamh.PA_AUTH_ERR

    if ( result[0] == False ):
        print 'No match found!'
        return pamh.PA_AUTH_ERR

    positionNumber = result[1]

    ## Gets all allowed users from config
    users = config.getItems('Users')

    ## Checks if matched positionNumber is assigned to user
    for user in users:

        if ( user[1] == str(positionNumber)):
            print 'Access granted.'
            return pamh.PAM_SUCCESS

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
