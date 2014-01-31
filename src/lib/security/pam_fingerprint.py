"""
"" PAM Fingerprint
"" PAM interface implementation
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved. 
"""

from pam_fingerprint.classes.Logger import *
from pam_fingerprint.classes.Config import *
from pam_fingerprint.libraries.Fingerprint import *

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

    print 'PAM_Fingerprint loading module...'

    ## Tries to init config instance
    try:
        config = Config('/etc/pam_fingerprint.conf')

    except Exception:
        print 'TODO: Config Exception message'
        return pamh.PAM_IGNORE

    ## Tries to init logger instance
    try:
        logger = Logger()

    except Exception:
        print 'TODO: Logger Exception message'
        return pamh.PAM_IGNORE

    ## Gets connection values
    port = config.readString('FingerprintModule', 'port')
    baudRate = config.readInteger('FingerprintModule', 'baudRate')
    address = config.readHex('FingerprintModule', 'address')
    password = config.readHex('FingerprintModule', 'password')

    ## Tries to establish connection
    try:
        fingerprint = Fingerprint(port, baudRate, address, password)

    except Exception:
        print 'TODO: Fingerprint sensor not found!'
        return pamh.PAM_IGNORE
        
    p = fingerprint.verifyPassword()

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.DEBUG, 'Sensor password is correct.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, 'Communication error')
        return pamh.PAM_IGNORE      
    elif ( p[0] == FINGERPRINT_PASSFAIL ):
        logger.log(Logger.ERROR,'Password is wrong')
        return pamh.PAM_AUTH_ERR
    else:
        logger.log(Logger.ERROR, 'Unknown error')
        return pamh.PAM_IGNORE

    p = [-1]
    logger.log(Logger.NOTICE, 'Waiting for finger...')

    while ( p[0] != FINGERPRINT_OK ):

        ## Gets fingerprint image
        p = fingerprint.getImage()

        if ( p[0] == FINGERPRINT_OK ):
            logger.log(Logger.NOTICE, 'Image taken.')
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            logger.log(Logger.ERROR, 'Communication error')
            return pamh.PAM_IGNORE
        elif ( p[0] == FINGERPRINT_NOFINGER ):
            ## Will be logged many times
            logger.log(Logger.DEBUG, 'No finger found')
        elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
            logger.log(Logger.ERROR, 'Imaging error')
            return pamh.PAM_IGNORE
        else:
            logger.log(Logger.ERROR, 'Unknown error')
            return pamh.PAM_IGNORE

    ## First step is done
    p = fingerprint.image2Tz(0x01);

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.DEBUG, 'Image converted.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, 'Communication error')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_IMAGEMESS ):
        logger.log(Logger.ERROR, 'Image too messy!')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
        logger.log(Logger.ERROR, 'Could not find fingerprint features')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
        logger.log(Logger.ERROR, 'Could not find fingerprint features')
        return pamh.PAM_IGNORE
    else:
        logger.log(Logger.ERROR, 'Unknown error')
        return pamh.PAM_IGNORE

    ## Searches fingerprint in database
    p = fingerprint.searchTemplate();

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.NOTICE, 'Found a match.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, 'Communication error')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_NOTFOUND ):
        logger.log(Logger.NOTICE, 'Did not found a match')
        return pamh.PAM_IGNORE
    else:
        logger.log(Logger.ERROR, 'Unknown error')
        return pamh.PAM_IGNORE

    positionNumber = p[1]
    positionNumber = utilities.leftShift(positionNumber, 8)
    positionNumber = positionNumber | p[2]

    # TODO: Check if user exists in a file
    if ( positionNumber > 0 ):
        return pamh.PAM_SUCCESS
    
    ## Denies for default 
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
