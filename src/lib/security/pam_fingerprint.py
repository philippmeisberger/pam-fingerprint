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

import hashlib
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

    ## Checks if the user is assigned to any hash
    try:
        expectedFingerprintHash = config.readString('Users', user)

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
        ## TODO: Change PyFingerprintConnection to PyFingerprint
        fingerprint = PyFingerprintConnection(port, baudRate, address, password)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')
    
    except (Exception, ValueError), e:
        logger.error('The fingerprint sensor could not be initialized!', exc_info=True)
        msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Sensor is not connected correctly!')
        pamh.conversation(msg)
        return pamh.PAM_IGNORE

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...')
    pamh.conversation(msg)

    ## Tries to read fingerprint
    try:
        while ( f.readImage() == False ):
            pass
    
        f.convertImage(0x01)
        
        result = f.searchTemplate()
        positionNumber = result[0]

        if ( positionNumber == -1 ):
            logger.info('No match found!')
            msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!')
            pamh.conversation(msg)
            return pamh.PAM_IGNORE

        f.loadTemplate(positionNumber, 0x01)
        characterics = f.downloadCharacteristics(0x01)
        
        fingerprintHash = hashlib.sha256(str(characterics)).hexdigest()

        if ( fingerprintHash == expectedFingerprintHash ):
            logger.info('Access granted!')
            msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access granted!')
            pamh.conversation(msg)
            return pamh.PAM_SUCCESS 
        else:
            logger.info('The found match is not assigned to user!')
            msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!')
            pamh.conversation(msg)
            return pamh.PA_AUTH_ERR
        
    except Exception, e:
        logger.error('Fingerprint read failed!', exc_info=True)
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
