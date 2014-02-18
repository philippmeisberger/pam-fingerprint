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
    "" @param integer address (4 bytes)
    "" @param integer password (4 bytes)
    "" @return void
    """
    def __init__(self, port, baudRate, address, password):

        self.__connection = PyFingerprintConnection(port, baudRate, address, password)

        if ( self.verifyPassword() == False ):
            raise ValueError('The fingerprint sensor password is not correct!')

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
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        p = self.__connection.setPassword(newPassword)

        ## DEBUG: Password set was successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        p = self.__connection.setAddress(newPassword)

        ## DEBUG: Address set was successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Unknown error
        return False

    """
    "" Sets a system parameter of the fingerprint sensor.
    ""
    "" @param integer parameterNumber (1 byte)
    "" @param integer parameterValue (1 byte)
    "" @return boolean
    """
    def setSystemParameter(self, parameterNumber, parameterValue):

        p = self.__connection.setSystemParameter(parameterNumber, parameterValue)

        ## DEBUG: Parameter set was successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Invalid register no?
        elif ( p[0] == FINGERPRINT_INVALIDREG ):
            return False

        ## DEBUG: Unknown error
        return False

    """
    "" Gets all system parameters of the fingerprint sensor.
    ""
    "" @return tuple (integer [2 bytes], integer [2 bytes], integer [2 bytes]) TODO
    """
    def getSystemParameters(self):

        p = self.__connection.getSystemParameters();

        ## DEBUG: Read successfully
        if ( p[0] == FINGERPRINT_OK ):

            statusRegister = p[1] << 8 | p[2]
            systemID = p[3] << 8 | p[4]
            storageCapacity = p[5] << 8 | p[6]
            securityLevel = p[7] << 8 | p[8]
            deviceAddress = ((p[9] << 8 | p[10]) << 8 | p[11]) << 8 | p[12]
            packetLength = p[13] << 8 | p[14]
            baudRate = p[15] << 8 | p[16]

            return (statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate)

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return (-1, -1, -1, -1, -1, -1, -1)

        ## DEBUG: Unknown error
        return (-1, -1, -1, -1, -1, -1, -1)

    """
    "" Gets the number of templates stored in database.
    ""
    "" @return integer
    """
    def getTemplateCount(self):

        p = self.__connection.getTemplateCount();

        ## DEBUG: Read successfully
        if ( p[0] == FINGERPRINT_OK ):
            templateCount = utilities.leftShift(p[1], 8) | p[2]
            return templateCount

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return -1

        ## DEBUG: Unknown error
        return -1









    """
    "" Reads the characteristics of a finger.
    ""
    "" @return boolean
    """
    def readImage(self):

        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            p = self.__connection.readImage()

            ## DEBUG: Image taken
            if ( p[0] == FINGERPRINT_OK ):
                return True

            ## DEBUG: Communication error
            elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
                return False

            ## DEBUG: No finger found
            elif ( p[0] == FINGERPRINT_NOFINGER ):
                continue

            ## DEBUG: Imaging error
            elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
                return False

            ## DEBUG: Unknown error
            else:
                return False

    """
    "" Converts the read finger characteristics and stores it temporarily in ImageBuffer1 or ImageBuffer2.
    ""
    "" @param integer bufferNumber (1 byte)
    "" @return boolean
    """
    def convertImage(self, bufferNumber = 1):

        p = self.__connection.convertImage(bufferNumber)

        ## DEBUG: Image converted
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Image is too messy
        elif ( p[0] == FINGERPRINT_IMAGEMESS ):
            return False

        ## DEBUG: Could not find fingerprint features
        elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
            return False

        ## DEBUG: Could not find fingerprint features
        elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
            return False

        ## DEBUG: Unknown error
        return False

    """
    "" Compares the finger characteristics of ImageBuffer1 with ImageBuffer2 and returns the accuracy score.
    ""
    "" @return integer
    """
    def compareTemplates(self):

        p = self.__connection.compareTemplates();

        ## DEBUG: Read successfully
        if ( p[0] == FINGERPRINT_OK ):
            accuracyScore = utilities.leftShift(p[1], 8) | p[2]
            return accuracyScore

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return -1

        ## DEBUG: The characteristics does not match
        elif ( p[0] == FINGERPRINT_NOMATCH ):
            return -1

        ## DEBUG: Unknown error
        return -1


    """
    "" Downloads the finger characteristics of ImageBuffer1 or ImageBuffer2
    ""
    "" @param integer bufferNumber (1 byte)
    "" @return TODO
    """
    ## TODO name
    def downloadTemplate(self, bufferNumber = 1):

        p = self.__connection.downloadTemplate(bufferNumber);

        ## DEBUG: Read successfully
        if ( p[0] == FINGERPRINT_OK ):

            return p

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return (-1,)

        ## DEBUG: Could not receive follow-up packet
        elif ( p[0] == FINGERPRINT_PACKETRESPONSEFAIL ):
            return (-1,)

        ## DEBUG: Unknown error
        return (-1,)




    """
    "" Combines the fingerprint characteristics temporarily stored in ImageBuffer1 and ImageBuffer2 to a template.
    "" The created template (the result) will be stored again in ImageBuffer1 and ImageBuffer2 as the same.
    ""
    "" @return tuple (integer [1 byte])
    """
    def createTemplate(self):

        p = self.__connection.createTemplate()

        ## DEBUG: Image converted
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Images not matching
        elif ( p[0] == FINGERPRINT_ENROLLMISMATCH ):
            return False

        ## DEBUG: Unknown error
        return False






    """
    "" Loads an existing template specified by position number to specified CharBuffer.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @param integer charBufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def loadTemplate(self, positionNumber, charBufferNumber = 0x01):

        p = self.__connection.loadTemplate(positionNumber, charBufferNumber)

        ## DEBUG: Read successful
        if ( p[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Read failed
        elif ( p[0] == FINGERPRINT_READFAILED ):
            return False

        ## DEBUG: Read failed
        elif ( p[0] == FINGERPRINT_OUTOFRANGE ):
            return False

        ## DEBUG: Unknown error
        return False






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

            elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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
    """
    def createTemplate(self):

        print 'Waiting for finger...'
        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            ## Gets fingerprint image
            p = self.__connection.getImage()

            if ( p[0] == FINGERPRINT_OK ):
                utilities.printDebug('Image taken')

            elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

            elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_BADLOCATION ):
            raise Exception('Could not store template in that location')

        elif ( p[0] == FINGERPRINT_FLASHERR ):
            raise Exception('Error writing to flash')

        else:
            raise Exception('Unknown error')

        return (True, positionNumber)
        """

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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
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

        elif ( p[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_DBCLEARFAIL ):
            utilities.printDebug('Could not clear template database')
            return False

        else:
            raise Exception('Unknown error')

        return False

## Tests
import hashlib

try:

    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except (Exception, ValueError) as e:
    print 'The fingerprint sensor could not be initialized!'
    print e.message
    
## Gets some sensor information
##

#print 'Currently stored templates: ' + str(f.getTemplateCount())
#print 'System parameters: ' + str(f.getSystemParameters())

#exit(0)


## Enrolls new finger
##

try:
    print 'Waiting for finger...'

    while ( f.readImage() == False ):
        pass
        
    f.convertImage(0x01)

    print 'Remove finger...'
    time.sleep(2)

    print 'Waiting for same finger again...'

    while ( f.readImage() == False ):
        pass
        
    f.convertImage(0x02)
    f.createTemplate()

    positionNumber = f.getTemplateCount()
    positionNumber = positionNumber + 1

    #print 'New position number #' + str(positionNumber)
    f.storeTemplate(positionNumber)

except:
    print 'Fingerprint enroll failed!'
    
## Gets hash of readed fingerprint
##

try:
    while ( f.readImage() == False ):
        pass
    
    f.convertImage(0x01)

    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber == -1 ):
        print 'No match found!'
    else:
        print 'Found template #' + str(positionNumber)

    f.loadTemplate(positionNumber, 0x01)
    characterics = f.downloadCharacteristics(0x01)
    
    print hashlib.sha256(str(characterics)).hexdigest()

except:
    print 'Fingerprint read failed!'
    
