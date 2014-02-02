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

    print 'pamfingerprint: loading module...'
    #print pamh.get_user()

    ## Tries to init Config
    try:
        config = Config('/etc/pam_fingerprint.conf')

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pam_fingerprint.log', logLevel)

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    ## Gets connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    ## Tries to check fingerprint
    try:
        result = fingerprint.checkFinger()

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    if ( result[0] == False ):
        print 'No match found!'
        return pamh.PAM_IGNORE

    positionNumber = result[1]

    ## Checks in config if <userName> matches <template ID>
    users = config.getItems('Users')

    for user in users:
        if ( config.readInteger(user) == positionNumber ):
            print 'Access granted for '+ user +'!'
            return pamh.PAM_SUCCESS

    ## Denies for default
    print 'Access denied!'
    return pamh.IGNORE

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

"""
"" PAM service function for account management.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_acct_mgmt(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
"" PAM service function to open session management.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_open_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
"" PAM service function to terminate session management.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_close_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
"" PAM service function for authentication token management.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_chauthtok(pamh, flags, argv):

    return pamh.PAM_SUCCESS
