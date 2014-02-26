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
        user = pamh.ruser
        
        if ( user == None ):
            user = pamh.get_user()            

        ## Be sure the user is set 
        if ( user == None ):
            logger.error('The user is not known!')
            return pamh.PAM_USER_UNKNOWN

    except (Exception, pamh.exception) as e:
        logger.error(e.message, exc_info=True)
        return pamh.PAM_USER_UNKNOWN

    ## Tries to init Config
    try:
        config = Config('/etc/pamfingerprint.conf')

    except Exception as e:
        logger.error(e.message, exc_info=True)
        return pamh.PAM_IGNORE

    logger.info('The user "' + user + '" is asking for permission for service "' + str(pamh.service) + '".')

    ## Checks if the the user was added in configuration
    if ( self.__config.itemExists('Users', userName) == False ):
        logger.error('The user was not added!')
        return pamh.PAM_IGNORE ## TODO: other flag?

    ## Tries to get user information (template position, fingerprint hash)
    try:
        userData = self.__config.readList('Users', userName)

        ## Validates user information
        if ( len(userData) != 2 ):
            raise ValueError('The user information of "' + userName + '" is invalid!')

        expectedPositionNumber = userData[0]
        expectedFingerprintHash = userData[1]

    except ValueError as e:
        logger.error(e.message, exc_info=False)
        return pamh.PAM_AUTH_ERR

    ## Gets sensor connection values
    port = config.readString('PyFingerprint', 'port')
    baudRate = config.readInteger('PyFingerprint', 'baudRate')
    address = config.readHex('PyFingerprint', 'address')
    password = config.readHex('PyFingerprint', 'password')

    ## Tries to init PyFingerprint
    try:
        fingerprint = PyFingerprint(port, baudRate, address, password)

        if ( fingerprint.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except (Exception, ValueError) as e:
        logger.error('The fingerprint sensor could not be initialized!', exc_info=True)
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Sensor initialization failed!'))
        return pamh.PAM_IGNORE

    msg = pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Waiting for finger...')
    pamh.conversation(msg)

    ## Tries to read fingerprint
    try:
        while ( fingerprint.readImage() == False ):
            pass

        fingerprint.convertImage(0x01)

        ## Gets position of template
        result = fingerprint.searchTemplate()
        positionNumber = result[0]

        ## Checks if the template position is invalid
        if ( positionNumber == -1 ):
            raise Exception('No match found!')

        ## Checks if the template position is correct
        if ( positionNumber != expectedPositionNumber ):
            raise Exception('The template position of the found match is not equal to the stored one!')

        ## Gets characteristics
        fingerprint.loadTemplate(positionNumber, 0x01)
        characterics = fingerprint.downloadCharacteristics(0x01)

        ## Calculates hash of template
        fingerprintHash = hashlib.sha256(str(characterics)).hexdigest()

        ## Checks if the calculated hash is equal to expected hash from user
        if ( fingerprintHash == expectedFingerprintHash ):
            logger.info('Access granted!')
            pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access granted!'))
            return pamh.PAM_SUCCESS
        else:
            logger.info('The found match is not assigned to user!')
            pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!'))
            return pamh.PAM_AUTH_ERR

    except Exception as e:
        logger.error('Fingerprint read failed: ' + e.message, exc_info=False)
        pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, 'pamfingerprint ' + VERSION + ': Access denied!'))
        return pamh.PAM_AUTH_ERR

    ## Denies for default
    return pamh.PAM_AUTH_ERR

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
