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

        if ( os.path.exists(port) == False ):
            raise Exception('The fingerprint sensor port "' + port + '" was not found!')

        ## TODO: verify other parameters

        self.__address = address
        self.__password = password

        ## Initializes connection
        self.__serial = serial.Serial(port, baudRate, serial.EIGHTBITS)

        self.__serial.close()
        self.__serial.open()

        self.__serial.timeout = 2

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
    "" @param integer address (4 bytes)
    "" @param integer packetType (1 byte)
    "" @param tuple (integer [1 byte], ...) packetPayload
    "" @return boolean
    """
    def __writePacket(self, address, packetType, packetPayload):

        ## TODO: address param senseless?
        ## TODO: verify parameters

        ## Writes header (one byte at once)
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 24)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 16)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 0)))

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

        return True

    """
    "" Receives a packet from fingerprint sensor.
    ""
    "" @return tuple (packetType, packetPayload)
    """
    def __readPacket(self):

        receivedFragment = ''
        receivedPacketData = []

        while ( receivedFragment != '\n' ):
            ## Reads one packet fragment and converts to integer byte
            receivedFragment = self.__serial.read()
            receivedByte = utilities.stringToByte(receivedFragment)
            receivedPacketData.append(receivedByte)

        ## Checks if the packet could be valid (the minimal packet size is 12 bytes)
        if ( len(receivedPacketData) < 12 ):
            raise Exception('The received packet length is to small!')

        ## Checks the packet header
        if ( receivedPacketData[0] != utilities.rightShift(FINGERPRINT_STARTCODE, 8) or receivedPacketData[1] != utilities.rightShift(FINGERPRINT_STARTCODE, 0) ):
            raise Exception('The received packet does not begin with a valid header!')

        packetType = receivedPacketData[6]

        ## Calculates packet length (combines the 2 length bytes)
        packetLength = utilities.leftShift(receivedPacketData[7], 8)
        packetLength = packetLength | utilities.leftShift(receivedPacketData[8], 0)

        ## Calculates checksum:
        ## checksum = packet type (1 byte) + packet length (2 bytes) + packet payload (n bytes)
        packetChecksum = packetType + receivedPacketData[7] + receivedPacketData[8]

        packetPayload = []

        ## Collects package payload (ignore the last 2 checksum bytes)
        for i in range(9, 9 + packetLength - 2):
            packetPayload.append(receivedPacketData[i])
            packetChecksum += receivedPacketData[i]

        ## Calculates checksum (combines the last 2 bytes)
        receivedChecksum = utilities.leftShift(receivedPacketData[-2], 8)
        receivedChecksum = receivedChecksum | utilities.leftShift(receivedPacketData[-1], 0)

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Sensor password is correct
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Sensor password is wrong
        elif ( receivedPacketPayload[0] == FINGERPRINT_PASSFAIL ):
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
            raise ValueError('The given password is not valid!')

        packetPayload = (
            FINGERPRINT_SETPASSWORD,
            utilities.rightShift(newPassword, 24),
            utilities.rightShift(newPassword, 16),
            utilities.rightShift(newPassword, 8),
            utilities.rightShift(newPassword, 0),
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Password set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
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
            raise ValueError('The given address is not valid!')

        packetPayload = (
            FINGERPRINT_SETADDRESS,
            utilities.rightShift(newAddress, 24),
            utilities.rightShift(newAddress, 16),
            utilities.rightShift(newAddress, 8),
            utilities.rightShift(newAddress, 0),
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Address set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        ## DEBUG: Communication error
        elif ( receivedPacketPayload[0] == FINGERPRINT_COMMUNICATIONERROR ):
            return False

        ## DEBUG: Unknown error
        return False


















    """
    "" Sets a system parameter of the fingerprint sensor.
    ""
    "" @param integer parameterNumber (1 byte)
    "" @param integer parameterValue (1 byte)
    "" @return tuple (integer [1 byte])
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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Gets all system parameters of the fingerprint sensor.
    ""
    "" @return tuple (integer [17 bytes])
    """
    def getSystemParameters(self):

        packetPayload = (
            FINGERPRINT_GETSYSTEMPARAMETERS,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Gets the number of stored templates.
    ""
    "" @return tuple (integer [3 bytes])
    """
    def getTemplateCount(self):

        packetPayload = (
            FINGERPRINT_TEMPLATECOUNT,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Reads the image of a finger and stores it in ImageBuffer.
    ""
    "" @return tuple (integer [1 byte])
    """
    def readImage(self):

        packetPayload = (
            FINGERPRINT_READIMAGE,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Converts the image in ImageBuffer to finger characteristics and stores in CharBuffer1 or CharBuffer2.
    ""
    "" @param integer charBufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def convertImage(self, charBufferNumber = 0x01):

        if ( charBufferNumber != 0x01 and charBufferNumber != 0x02 ):
            raise ValueError('The given char buffer number is not valid!')

        packetPayload = (
            FINGERPRINT_CONVERTIMAGE,
            charBufferNumber,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload


















    """
    "" Compares the finger characteristics of CharBuffer1 with CharBuffer2 and returns the accuracy score.
    ""
    "" @return tuple (integer [3 bytes])
    """
    def compareCharacteristics(self):

        packetPayload = (
            FINGERPRINT_COMPARECHARACTERISTICS,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload


    ## TODO: uploadCharacteristics()

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Clears the complete template database.
    ""
    "" @return tuple (integer [1 byte])
    """
    def clearDatabase(self):

        packetPayload = (
            FINGERPRINT_CLEARDATABASE,
        )

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

    """
    "" Search the finger characteristiccs in CharBuffer in database.
    ""
    "" @return tuple (integer [5 bytes])
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

        self.__writePacket(self.__address, FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload

## Tests
##

f = PyFingerprintConnection()

print f.verifyPassword()

#print f.downloadCharacteristics()