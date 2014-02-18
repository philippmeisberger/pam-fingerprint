"""
"" PyFingerprintConnection
"" A python written library for an UART optical fingerprint sensor.
""
"" Requirements:
"" ~# apt-get install python-serial
""
"" Inspired by Adafruit Industries
"" @see https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library
""
"" Copyright 2014 Bastian Raschke.
"" All rights reserved.
""
"""

from includes.constants import *
import includes.utilities as utilities

import serial
import struct
import os.path


class PyFingerprintConnection(object):

    """
    "" Address to connect to sensor
    "" @var integer __address (32 bit)
    """
    __address = None

    """
    "" Password to connect to sensor
    "" @var integer __password (32 bit)
    """
    __password = None

    """
    "" UART serial connection via PySerial
    "" @var Serial __serial
    """
    __serial = None

    """
    "" Constructor
    ""
    "" @param string port
    "" @param integer baudRate
    "" @param integer address (4 bytes)
    "" @param integer password (4 bytes)
    "" @return void
    """
    def __init__(self, port = '/dev/ttyUSB0', baudRate = 57600, address = 0xFFFFFFFF, password = 0x00000000):

        ## Validates port
        if ( os.path.exists(port) == False ):
            raise Exception('The fingerprint sensor port "' + port + '" was not found!')

        ## Validates the baud rate
        if ( baudRate < 9600 or baudRate > 115200 or baudRate % 9600 != 0 ):
            raise Exception('The given baud rate is not valid!')

        ## Validates the address
        if ( address < 0x00000000 or address > 0xFFFFFFFF ):
            raise ValueError('The given address is not valid!')

        ## Validates the password
        if ( password < 0x00000000 or password > 0xFFFFFFFF ):
            raise ValueError('The given password is not valid!')

        self.__address = address
        self.__password = password

        ## Initializes connection
        self.__serial = serial.Serial(port = port, baudrate = baudRate, bytesize = serial.EIGHTBITS, timeout = 2)
        self.__serial.close()
        self.__serial.open()

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        ## Closes connection if established
        if ( self.__serial != None ):
            self.__serial.close()

    """
    "" Sends a packet to fingerprint sensor.
    ""
    "" @param integer packetType (1 byte)
    "" @param tuple<integer [1 byte]> packetPayload
    "" @return void
    """
    def __writePacket(self, packetType, packetPayload):

        ## Writes header (one byte at once)
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__serial.write(utilities.byteToString(utilities.rightShift(self.__address, 24)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(self.__address, 16)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(self.__address, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(self.__address, 0)))

        self.__serial.write(utilities.byteToString(packetType))

        ## The packet length = package payload (n bytes) + checksum (2 bytes)
        packetLength = len(packetPayload) + 2

        self.__serial.write(utilities.byteToString(utilities.rightShift(packetLength, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(packetLength, 0)))

        ## The packet checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
        packetChecksum = packetType + utilities.rightShift(packetLength, 8) + utilities.rightShift(packetLength, 0)

        ## Writes payload
        for i in range(0, len(packetPayload)):
            self.__serial.write(utilities.byteToString(packetPayload[i]))
            packetChecksum += packetPayload[i]

        ## Writes checksum (2 bytes)
        self.__serial.write(utilities.byteToString(utilities.rightShift(packetChecksum, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(packetChecksum, 0)))

    """
    "" Receives a packet from fingerprint sensor.
    ""
    "" @return tuple (packetType, packetPayload)
    """
    def __readPacket(self):

        receivedPacketData = []
        i = 0

        while ( True ):

            ## Reads one byte
            receivedFragment = self.__serial.read()

            if ( len(receivedFragment) != 0 ):
                receivedFragment = utilities.stringToByte(receivedFragment)
                ## print 'Received packet fragment = ' + hex(receivedFragment)

            ## Inserts byte if packet seems valid
            receivedPacketData.insert(i, receivedFragment)
            i += 1

            ## Packet could be complete (the minimal packet size is 12 bytes)
            if ( i >= 12 ):

                ## Checks the packet header
                if ( receivedPacketData[0] != utilities.rightShift(FINGERPRINT_STARTCODE, 8) or receivedPacketData[1] != utilities.rightShift(FINGERPRINT_STARTCODE, 0) ):
                    raise Exception('The received packet does not begin with a valid header!')

                ## Calculates packet payload length (combines the 2 length bytes)
                packetPayloadLength = utilities.leftShift(receivedPacketData[7], 8)
                packetPayloadLength = packetPayloadLength | utilities.leftShift(receivedPacketData[8], 0)

                ## Checks if the packet is still fully received
                ## Condition: index counter < packet payload length + packet frame
                if ( i < packetPayloadLength + 9 ):
                    continue

                ## At this point the packet should be fully received

                packetType = receivedPacketData[6]

                ## Calculates checksum:
                ## checksum = packet type (1 byte) + packet length (2 bytes) + packet payload (n bytes)
                packetChecksum = packetType + receivedPacketData[7] + receivedPacketData[8]

                packetPayload = []

                ## Collects package payload (ignore the last 2 checksum bytes)
                for j in range(9, 9 + packetPayloadLength - 2):
                    packetPayload.append(receivedPacketData[j])
                    packetChecksum += receivedPacketData[j]

                ## Calculates full checksum of the 2 separate checksum bytes
                receivedChecksum = utilities.leftShift(receivedPacketData[i - 2], 8)
                receivedChecksum = receivedChecksum | utilities.leftShift(receivedPacketData[i - 1], 0)

                if ( receivedChecksum != packetChecksum ):
                    raise Exception('The received packet is corrupted (the checksum is wrong)!')

                return (packetType, packetPayload)

    """
    "" Verifies password of the fingerprint sensor.
    ""
    "" @return boolean
    """
    def verifyPassword(self):

        packetPayload = (
            FINGERPRINT_VERIFYPASSWORD,
            utilities.rightShift(self.__password, 24),
            utilities.rightShift(self.__password, 16),
            utilities.rightShift(self.__password, 8),
            utilities.rightShift(self.__password, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Sensor password is correct
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_WRONGPASSWORD ):
            return False

        else:
            raise Exception('Unknown error')

    """
    "" Sets the password of the fingerprint sensor.
    ""
    "" @param integer newPassword (4 bytes)
    "" @return boolean
    """
    def setPassword(self, newPassword):

        ## Validates the password (maximum 4 bytes)
        if ( newPassword < 0x00000000 or newPassword > 0xFFFFFFFF ):
            raise ValueError('The given password is not valid!')

        packetPayload = (
            FINGERPRINT_SETPASSWORD,
            utilities.rightShift(newPassword, 24),
            utilities.rightShift(newPassword, 16),
            utilities.rightShift(newPassword, 8),
            utilities.rightShift(newPassword, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Password set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error')

    """
    "" Sets the module address of the fingerprint sensor.
    ""
    "" @param integer newAddress (4 bytes)
    "" @return boolean
    """
    def setAddress(self, newAddress):

        ## Validates the address (maximum 4 bytes)
        if ( newAddress < 0x00000000 or newAddress > 0xFFFFFFFF ):
            raise ValueError('The given address is not valid!')

        packetPayload = (
            FINGERPRINT_SETADDRESS,
            utilities.rightShift(newAddress, 24),
            utilities.rightShift(newAddress, 16),
            utilities.rightShift(newAddress, 8),
            utilities.rightShift(newAddress, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Address set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error')

    """
    "" Sets a system parameter of the fingerprint sensor.
    ""
    "" @param integer parameterNumber (1 byte)
    "" @param integer parameterValue (1 byte)
    "" @return boolean
    """
    def setSystemParameter(self, parameterNumber, parameterValue):

        ## Validates the baudrate parameter
        if ( parameterNumber == 4 ):

            if ( parameterValue < 1 or parameterValue > 12 ):
                raise ValueError('The given baudrate parameter is not valid!')

        ## Validates the security level parameter
        elif ( parameterNumber == 5 ):

            if ( parameterValue < 1 or parameterValue > 5 ):
                raise ValueError('The given security level parameter is not valid!')

        ## Validates the package length parameter
        elif ( parameterNumber == 6 ):

            if ( parameterValue < 0 or parameterValue > 3 ):
                raise ValueError('The given package length parameter is not valid!')

        ## The parameter number is not valid
        else:
            raise ValueError('The given parameter is not valid!')

        packetPayload = (
            FINGERPRINT_SETSYSTEMPARAMETER,
            parameterNumber,
            parameterValue,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Parameter set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_INVALIDREGISTER ):
            raise Exception('Invalid register number')

        else:
            raise Exception('Unknown error')

    """
    "" Gets all system parameters of the fingerprint sensor.
    ""
    "" @return
    """
    def getSystemParameters(self):

        packetPayload = (
            FINGERPRINT_GETSYSTEMPARAMETERS,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read successfully
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

            statusRegister     = utilities.leftShift(receivedPacketPayload[1], 8) | utilities.leftShift(receivedPacketPayload[2], 0)
            systemID           = utilities.leftShift(receivedPacketPayload[3], 8) | utilities.leftShift(receivedPacketPayload[4], 0)
            storageCapacity    = utilities.leftShift(receivedPacketPayload[5], 8) | utilities.leftShift(receivedPacketPayload[6], 0)
            securityLevel      = utilities.leftShift(receivedPacketPayload[7], 8) | utilities.leftShift(receivedPacketPayload[8], 0)
            deviceAddress      = ((receivedPacketPayload[9] << 8 | receivedPacketPayload[10]) << 8 | receivedPacketPayload[11]) << 8 | receivedPacketPayload[12]
            packetLength       = utilities.leftShift(receivedPacketPayload[13], 8) | utilities.leftShift(receivedPacketPayload[14], 0)
            baudRate           = utilities.leftShift(receivedPacketPayload[15], 8) | utilities.leftShift(receivedPacketPayload[16], 0)

            return (statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate)

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error')

    ## TODO: implement ReadConList()

    """
    "" Gets the number of stored templates.
    ""
    "" @return integer
    """
    def getTemplateCount(self):

        packetPayload = (
            FINGERPRINT_TEMPLATECOUNT,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read successfully
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            templateCount = utilities.leftShift(receivedPacketPayload[1], 8)
            templateCount = templateCount | utilities.leftShift(receivedPacketPayload[2], 0)
            return templateCount

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error')

    """
    "" Reads the image of a finger and stores it in ImageBuffer.
    ""
    "" @return boolean
    """
    def readImage(self):

        packetPayload = (
            FINGERPRINT_READIMAGE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Image read successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_NOFINGER ):
            return False

        elif ( receivedPacketPayload[0] == FINGERPRINT_IMAGEERROR ):
            raise Exception('Imaging error')

        else:
            raise Exception('Unknown error')

    ## TODO: implement: uploadImage()
    ## TODO: implement: downloadImage()

    """
    "" Converts the image in ImageBuffer to finger characteristics and stores in CharBuffer1 or CharBuffer2.
    ""
    "" @param integer charBufferNumber (1 byte)
    "" @return boolean
    """
    def convertImage(self, charBufferNumber = 0x01):

        if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
            raise ValueError('The given char buffer number is not valid!')

        packetPayload = (
            FINGERPRINT_CONVERTIMAGE,
            charBufferNumber,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Image converted
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_MESSYIMAGE ):
            raise Exception('The image is too messy')

        elif ( receivedPacketPayload[0] == FINGERPRINT_FEATUREFAIL ):
            raise Exception('Could not find fingerprint features')

        elif ( receivedPacketPayload[0] == FINGERPRINT_INVALIDIMAGE ):
            raise Exception('Could not find fingerprint features')

        else:
            raise Exception('Unknown error')

    """
    "" Combines the fingerprint characteristics which are stored in CharBuffer1 and CharBuffer2 to a template.
    "" The created template will be stored again in CharBuffer1 and CharBuffer2 as the same.
    ""
    "" @return tuple (integer [1 byte])
    """
    def createTemplate(self):

        packetPayload = (
            FINGERPRINT_CREATETEMPLATE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template created successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        ## DEBUG: The images not matching
        elif ( receivedPacketPayload[0] == FINGERPRINT_ENROLLMISMATCH ):
            return False

        else:
            raise Exception('Unknown error')

    """
    "" Saves a template from the specified CharBuffer to the given position number.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @param integer charBufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def storeTemplate(self, positionNumber, charBufferNumber = 0x01):

        if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
            raise ValueError('The given position number is not valid!')

        if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
            raise ValueError('The given char buffer number is not valid!')

        packetPayload = (
            FINGERPRINT_STORETEMPLATE,
            charBufferNumber,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template stored successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_BADLOCATION ):
            raise Exception('Could not store template in that location')

        elif ( receivedPacketPayload[0] == FINGERPRINT_FLASHERROR ):
            raise Exception('Error writing to flash')

        else:
            raise Exception('Unknown error')

    """
    "" Loads an existing template specified by position number to specified CharBuffer.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @param integer charBufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def loadTemplate(self, positionNumber, charBufferNumber = 0x01):

        if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
            raise ValueError('The given position number is not valid!')

        if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
            raise ValueError('The given char buffer number is not valid!')

        packetPayload = (
            FINGERPRINT_LOADTEMPLATE,
            charBufferNumber,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template loaded successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_READERROR ):
            raise Exception('Template read error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_OUTOFRANGE ):
            raise Exception('The template position is out of range')

        else:
            raise Exception('Unknown error')

    """
    "" Deletes one template from fingerprint database.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @return tuple (integer [1 byte])
    """
    def deleteTemplate(self, positionNumber):

        if ( positionNumber < 0x0000 or positionNumber > 0x00A3 ):
            raise ValueError('The given position number is not valid!')

        ## Deletes only one template
        count = 0x0001

        packetPayload = (
            FINGERPRINT_DELETETEMPLATE,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
            utilities.rightShift(count, 8),
            utilities.rightShift(count, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template deleted successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_DELETEERROR ):
            raise Exception('Could not delete template')

        else:
            raise Exception('Unknown error')

    """
    "" Clears the complete template database.
    ""
    "" @return tuple (integer [1 byte])
    """
    def clearDatabase(self):

        packetPayload = (
            FINGERPRINT_CLEARDATABASE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Database cleared successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_CLEARERROR ):
            raise Exception('Could not clear database')

        else:
            raise Exception('Unknown error')

    """
    "" Search the finger characteristiccs in CharBuffer in database.
    ""
    "" @return tuple (positionNumber, accuracyScore)
    """
    def searchTemplate(self):

        ## CharBuffer1 and CharBuffer2 are the same in this case
        charBufferNumber = 0x01

        ## Begin search at page 0x0000 for 0x00A3 (means 163) templates
        positionStart = 0x0000
        templatesCount = 0x00A3

        packetPayload = (
            FINGERPRINT_SEARCHTEMPLATE,
            charBufferNumber,
            utilities.rightShift(positionStart, 8),
            utilities.rightShift(positionStart, 0),
            utilities.rightShift(templatesCount, 8),
            utilities.rightShift(templatesCount, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Found template
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

            positionNumber = utilities.leftShift(receivedPacketPayload[1], 8)
            positionNumber = positionNumber | utilities.leftShift(receivedPacketPayload[2], 0)

            accuracyScore = utilities.leftShift(receivedPacketPayload[3], 8)
            accuracyScore = accuracyScore | utilities.leftShift(receivedPacketPayload[4], 0)

            return (positionNumber, accuracyScore)

        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_NOMATCHFOUND ):
            return (-1, -1)

        else:
            raise Exception('Unknown error')














    """
    "" Compares the finger characteristics of CharBuffer1 with CharBuffer2 and returns the accuracy score.
    ""
    "" @return tuple (integer [3 bytes])
    """
    def compareCharacteristics(self):

        packetPayload = (
            FINGERPRINT_COMPARECHARACTERISTICS,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    ## TODO: implement: uploadCharacteristics()

    """
    "" Downloads the finger characteristics of CharBuffer1 or CharBuffer2.
    ""
    "" @param integer charBufferNumber (1 byte)
    "" @return tuple (integer [3 bytes])
    """
    def downloadCharacteristics(self, charBufferNumber = 0x01):

        if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
            raise ValueError('The given char buffer number is not valid!')

        packetPayload = (
            FINGERPRINT_DOWNLOADCHARACTERISTICS,
            charBufferNumber,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        ## Gets first reply packet
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        completePacketData = [
            receivedPacketPayload[0],
        ]

        ## Gets follow-up data packets until the last data packet is received
        while ( receivedPacketType != FINGERPRINT_ENDDATAPACKET ):

            receivedPacket = self.__readPacket()

            receivedPacketType = receivedPacket[0]
            receivedPacketPayload = receivedPacket[1]

            if ( receivedPacketType != FINGERPRINT_DATAPACKET and receivedPacketType != FINGERPRINT_ENDDATAPACKET ):
                raise Exception('The received packet is no data packet!')

            for i in range(0, len(receivedPacketPayload)):
                completePacketData.append(receivedPacketPayload[i])

        return completePacketData





## Tests
##

f = PyFingerprintConnection()
#print f.verifyPassword()

f.loadTemplate(0x0001, 0x01)
l = f.downloadCharacteristics(0x01)

#import hashlib
#print hashlib.sha256(str(l[1:])).hexdigest()
