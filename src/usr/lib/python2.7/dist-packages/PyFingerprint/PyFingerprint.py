"""
"" PyFingerprint
"" A python written interface to communicate easily with an UART optical fingerprint sensor.
""
"" Copyright 2014 Bastian Raschke.
"" All rights reserved.
""
"""

import includes.utilities as utilities
from includes.constants import *
from PyFingerprintConnection import *

import time


class PyFingerprint(object):

    """
    "" The PyFingerprintConnection instance
    "" @var PyFingerprintConnection __connection
    """
    __connection = None

    """
    "" Constructor
    ""
    "" @param string port
    "" @param integer baudRate
    "" @param integer address (32 bit)
    "" @param integer password (32 bit)
    "" @return void
    """
    def __init__(self, port, baudRate, address, password):

        self.__connection = PyFingerprintConnection(port, baudRate, address, password)

        if ( self.verifyPassword() == False ):
            raise Exception('The fingerprint sensor password is not correct!')

    """
    "" Verifies password of the fingerprint sensor.
    ""
    "" @return boolean
    """
    def verifyPassword(self):

        p = self.__connection.verifyPassword()

        ## DEBUG: Sensor password is correct
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            return False

        ## DEBUG: Sensor password is wrong
        elif ( p[0] == FINGERPRINT_PASSFAIL ):
            return False

        ## DEBUG: Unknown error
        return False

    """
    "" Sets the password of the fingerprint sensor.
    ""
    "" @param integer newPassword (4 bytes)
    "" @return boolean
    """
    def setPassword(self, newPassword):

        ## Validates the password (maximum 4 bytes)
        if ( newPassword < 0x00000000 or newPassword > 0xFFFFFFFF ):
            raise Exception('The given password is not valid!')

        p = self.__connection.setPassword(newPassword)

        ## DEBUG: Password set was successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            return False

        ## DEBUG: Unknown error
        return False

    """
    "" Sets the module address of the fingerprint sensor.
    ""
    "" @param integer newAddress (4 bytes)
    "" @return boolean
    """
    def setAddress(self, newAddress):

        ## Validates the address (maximum 4 bytes)
        if ( newAddress < 0x00000000 or newAddress > 0xFFFFFFFF ):
            raise Exception('The given address is not valid!')

        p = self.__connection.setAddress(newPassword)

        ## DEBUG: Password set was successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            return False

        ## DEBUG: Unknown error
        return False

    ## TODO:
    ## def getSystemParameters(self):

    """
    "" Gets the number of templates stored in database.
    ""
    "" @return integer
    """
    def getTemplateCount(self):

        p = self.__connection.getTemplateCount();

        ## DEBUG: Read successfully
        if ( p[0] == FINGERPRINT_OK ):

            templateCount = p[1]
            templateCount = utilities.leftShift(templateCount, 8)
            templateCount = templateCount | p[2]

            return templateCount

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            return -1

        ## DEBUG: Unknown error
        return -1



















    """
    "" Search for a finger template.
    ""
    "" @return tuple (boolean, integer)
    """
    def searchTemplate(self):

        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            ## Gets fingerprint image
            p = self.__connection.getImage()

            if ( p[0] == FINGERPRINT_OK ):
                utilities.printDebug('Image taken')

            elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
                raise Exception('Communication error')

            elif ( p[0] == FINGERPRINT_NOFINGER ):
                utilities.printDebug('No finger found')

            elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
                raise Exception('Imaging error')

            else:
                raise Exception('Unknown error')

        ## First step is done
        p = self.__connection.image2Tz(0x01);

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Image converted')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_IMAGEMESS ):
            raise Exception('Image is too messy')

        elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
            raise Exception('Could not find fingerprint features')

        elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
            raise Exception('Could not find fingerprint features')

        else:
            raise Exception('Unknown error')

        ## Searches fingerprint in database
        p = self.__connection.searchTemplate();

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Found a match')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_NOTFOUND ):
            utilities.printDebug('Did not found a match')
            return (False, -1)

        else:
            raise Exception('Unknown error')

        positionNumber = p[1]
        positionNumber = utilities.leftShift(positionNumber, 8)
        positionNumber = positionNumber | p[2]

        return (True, positionNumber)

    """
    "" Creates a new finger template.
    ""
    "" @return tuple (boolean, integer)
    """
    def createTemplate(self):

        print 'Waiting for finger...'
        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            ## Gets fingerprint image
            p = self.__connection.getImage()

            if ( p[0] == FINGERPRINT_OK ):
                utilities.printDebug('Image taken')

            elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
                raise Exception('Communication error')

            elif ( p[0] == FINGERPRINT_NOFINGER ):
                utilities.printDebug('No finger found')

            elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
                raise Exception('Imaging error')

            else:
                raise Exception('Unknown error')

        ## First step is done
        p = self.__connection.convertImage(0x01);

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Image converted')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_IMAGEMESS ):
            raise Exception('Image is too messy')

        elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
            raise Exception('Could not find fingerprint features')

        elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
            raise Exception('Could not find fingerprint features')

        else:
            raise Exception('Unknown error')

        print 'Remove finger...'
        time.sleep(2)

        p = [-1]

        ## Waiting the user removes finger
        while ( p[0] != FINGERPRINT_NOFINGER ):
            p = self.__connection.getImage()

        print 'Waiting for same finger again...'
        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            ## Gets fingerprint image
            p = self.__connection.getImage()

            if ( p[0] == FINGERPRINT_OK ):
                utilities.printDebug('Image taken')

            elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
                raise Exception('Communication error')

            elif ( p[0] == FINGERPRINT_NOFINGER ):
                utilities.printDebug('No finger found')

            elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
                raise Exception('Imaging error')

            else:
                raise Exception('Unknown error')

        ## Second step is done
        p = self.__connection.convertImage(0x02);

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Image converted')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_IMAGEMESS ):
            raise Exception('Image is too messy')

        elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
            raise Exception('Could not find fingerprint features')

        elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
            raise Exception('Could not find fingerprint features')

        else:
            raise Exception('Unknown error')

        ## Creates template
        p = self.__connection.createTemplate()

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Images matching')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_ENROLLMISMATCH ):
            utilities.printDebug('Images not matching')
            return (False, -1)

        else:
            raise Exception('Unknown error')

        ## Stores fingerprint image in sensor database
        positionNumber = self.getTemplateCount() + 1
        p = self.__connection.storeTemplate(0x01, positionNumber)

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Template stored successfully')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_BADLOCATION ):
            raise Exception('Could not store template in that location')

        elif ( p[0] == FINGERPRINT_FLASHERR ):
            raise Exception('Error writing to flash')

        else:
            raise Exception('Unknown error')

        return (True, positionNumber)

    """
    "" Deletes a template from sensor database.
    ""
    "" @param integer positionNumber
    "" @return boolean
    """
    def deleteTemplate(self, positionNumber):

        p = self.__connection.deleteTemplate(positionNumber)

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Template deleted successfully')
            return True

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_DELETEFAIL ):
            utilities.printDebug('Could not delete template')
            return False

        else:
            raise Exception('Unknown error')

        return False

    """
    "" Deletes the complete sensor database.
    ""
    "" @return boolean
    """
    def deleteDatabase(self):

        p = self.__connection.clearDatabase()

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Template database cleared successfully')
            return True

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_DBCLEARFAIL ):
            utilities.printDebug('Could not clear template database')
            return False

        else:
            raise Exception('Unknown error')

        return False

## Tests:

#f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
#print 'Currently stored templates: ' + str(f.getTemplateCount())


#f.deleteDatabase()

#f.createTemplate()
#print f.searchTemplate()
