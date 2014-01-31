"""
"" PAM Fingerprint
"" PAM interface implementation
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved. 
"""
print 'pre'
#import os
#os.environ['PYTHONPATH'].append('/media/PM/PMCW/Dev/PamFingerprint/src')
#print 'post'

print 'pre logger import'
from pam_fingerprint.classes.Logger import *
print 'pre config import'
from pam_fingerprint.classes.Config import *
print 'pre fingerprint import'
from pam_fingerprint.libraries.Fingerprint import *

"""
"" Is called when a user tries to authenticate.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_authenticate(pamh, flags, argv):

    print 'PAM_Fingerprint loading module...'

    ## Inits config instance
    config = config
    
    ## Inits logger instance
    logger = Logger()
    
    ## Gets connection values
    port = config.readString('FingerprintModule', 'port')
    baudRate = config.readInteger('FingerprintModule', 'baudRate')
    address = config.readHex('FingerprintModule', 'address')
    password = config.readHex('FingerprintModule', 'password')

    ## Tries to establish connection
    fingerprint = Fingerprint(port, baudRate, address, password)

    print 'after establish'
    p = fingerprint.verifyPassword()

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.DEBUG, __name__, 'Sensor password is correct.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, __name__, 'Communication error')
        return pamh.PAM_IGNORE      
    elif ( p[0] == FINGERPRINT_PASSFAIL ):
        raise logger.log(Logger.ERROR, __name__,'Password is wrong')
        return pamh.PAM_AUTH_ERR
    else:
        logger.log(Logger.ERROR, __name__, 'Unknown error')
        return pamh.PAM_IGNORE

    p = [-1]
    logger.log(Logger.NOTICE, __name__, 'Waiting for finger...')

    while ( p[0] != FINGERPRINT_OK ):

        ## Gets fingerprint image
        p = fingerprint.getImage()

        if ( p[0] == FINGERPRINT_OK ):
            logger.log(Logger.NOTICE, __name__, 'Image taken.')
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            logger.log(Logger.ERROR, __name__, 'Communication error')
            return pamh.PAM_IGNORE
        elif ( p[0] == FINGERPRINT_NOFINGER ):
            ## Will be logged many times
            logger.log(Logger.WARNING, __name__, 'No finger found')
        elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
            logger.log(Logger.ERROR, __name__, 'Imaging error')
            return pamh.PAM_IGNORE
        else:
            logger.log(Logger.ERROR, __name__, 'Unknown error')
            return pamh.PAM_IGNORE

    ## First step is done
    p = fingerprint.image2Tz(0x01);

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.DEBUG, __name__, 'Image converted.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, __name__, 'Communication error')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_IMAGEMESS ):
        logger.log(Logger.ERROR, __name__, 'Image too messy!')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
        logger.log(Logger.ERROR, __name__, 'Could not find fingerprint features')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
        logger.log(Logger.ERROR, __name__, 'Could not find fingerprint features')
        return pamh.PAM_IGNORE
    else:
        logger.log(Logger.ERROR, __name__, 'Unknown error')
        return pamh.PAM_IGNORE

    ## Searches fingerprint in database
    p = fingerprint.searchTemplate();

    if ( p[0] == FINGERPRINT_OK ):
        logger.log(Logger.NOTICE, __name__, 'Found a match.')
    elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
        logger.log(Logger.ERROR, __name__, 'Communication error')
        return pamh.PAM_IGNORE
    elif ( p[0] == FINGERPRINT_NOTFOUND ):
        logger.log(Logger.NOTICE, __name__, 'Did not found a match')
        return pamh.PAM_IGNORE
    else:
        logger.log(Logger.ERROR, __name__, 'Unknown error')
        return pamh.PAM_IGNORE

    positionNumber = p[1]
    positionNumber = utilities.leftShift(positionNumber, 8)
    positionNumber = positionNumber | p[2]

    # TODO: Check if user exists in a file
    if ( positionNumber > 0 ):
        return pamh.PAM_SUCCESS
    
    ## Fallback: 
    return pamh.IGNORE

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_setcred(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_acct_mgmt(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_open_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_close_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_chauthtok(pamh, flags, argv):

    return pamh.PAM_SUCCESS

# Tests:
#pam_sm_authenticate('', '', '')
