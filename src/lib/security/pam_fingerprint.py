"""
"" PAM Fingerprint
"" PAM interface implementation
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved. 
"""
print 'sudo test1'
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
    
    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    ## Tries to init Logger
    try:
        logLevel = config.readInteger('Logger', 'level')
        logger = Logger('/var/log/pamfingerprint.log', logLevel)

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
        result = fingerprint.searchTemplate()

    except Exception as e:
        print e
        return pamh.PAM_IGNORE

    if ( result[0] == False ):
        print 'No match found!'
        return pamh.PA_AUTH_ERR

    positionNumber = result[1]

    ## Gets all tuples <userName> = <template ID> from config
    users = config.getItems('Users')

    ## Checks in config if <userName> matches <template ID>
    for user in users:
        if ( config.readInteger('Users', user[0]) == positionNumber ):
            print 'Access granted for user '+ user[0] +'!'
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
