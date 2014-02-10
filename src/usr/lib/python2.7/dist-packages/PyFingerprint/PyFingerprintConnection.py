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
    "" @param integer address (32 bit)
    "" @param integer password (32 bit)
    "" @return void
    """
    def __init__(self, port = '/dev/ttyUSB0', baudRate = 57600, address = 0xFFFFFFFF, password = 0x00000000):

        if ( os.path.exists(port) == False ):
            raise Exception('The fingerprint sensor port "' + port + '" was not found!')

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
        if ( self.__serial ):
            self.__serial.close()

    """
    "" Sends a packet to fingerprint sensor.
    ""
    "" @param integer address (4 bytes)
    "" @param integer packetType (1 byte)
    "" @param integer length (2 byte)
    "" @param tuple (integer [1 byte], ...) packetData
    "" @return boolean
    """
    def writePacket(self, address, packetType, length, packetData):

        ## Writes header (one byte at once)
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 24)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 16)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(address, 0)))

        self.__serial.write(utilities.byteToString(packetType))

        self.__serial.write(utilities.byteToString(utilities.rightShift(length, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(length, 0)))

        ## Calculates checksum:
        ## checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
        checksum = packetType + utilities.rightShift(length, 8) + utilities.rightShift(length, 0)

        ## Writes payload
        for i in range(0, len(packetData)):
            self.__serial.write(utilities.byteToString(packetData[i]))
            checksum += packetData[i]

        ## Writes checksum (2 bytes)
        self.__serial.write(utilities.byteToString(utilities.rightShift(checksum, 8)))
        self.__serial.write(utilities.byteToString(utilities.rightShift(checksum, 0)))

        return True

    """
    "" Receives a packet from fingerprint sensor.
    ""
    "" @return mixed
    """
    def readPacket(self):

        received = []
        index = 0

        while True:

            ## Reads one byte
            read = self.__serial.read()

            if ( len(read) != 0 ):

                ## Deep DEBUG
                ## utilities.printDebug('Received packet fragment ' + str(index) + ' = '+ str(struct.unpack('@c', read)[0]))
                read = utilities.stringToByte(read)

            ## Skips loop if first byte is not valid
            if (index == 0 and read != utilities.rightShift(FINGERPRINT_STARTCODE, 8)):
                continue

            ## Inserts byte if packet seems valid
            received.insert(index, read)
            index += 1

            ## Packet could be complete (minimal packet size are 9 bytes)
            if (index >= 9):

                ## Give up if first and second byte are not the startcode
                if ( received[0] != utilities.rightShift(FINGERPRINT_STARTCODE, 8) or received[1] != utilities.rightShift(FINGERPRINT_STARTCODE, 0) ):

                    ## Deep DEBUG
                    ## utilities.printDebug('Packet is corrupted (FINGERPRINT_STARTCODE not found)!')
                    return False

                ## Calculates length of the 2 length bytes
                length = received[7]
                length = utilities.leftShift(length, 8)
                length = length | received[8]

                ## Subtracts 2 bytes of packet (checksum)
                length = length - 2

                ## Continue to next loop if the packet is still not fully received
                if ( index <= length + 10 ):
                    continue

                ## Deep DEBUG
                ## utilities.printDebug('Packet length: ' + str(length))

                packetType = received[6]

                ## Calculates checksum:
                ## checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
                checksum = packetType + received[7] + received[8]

                packetData = []

                ## Build package payload
                for i in range(9, length + 9):
                    packetData.append(received[i])
                    checksum += received[i]

                ## Deep DEBUG
                ## utilities.printDebug('Packet calculated checksum: ' + str(checksum))

                ## Calculates full checksum of the 2 separate checksum bytes
                receivedChecksum = received[index - 2]
                receivedChecksum = utilities.leftShift(receivedChecksum, 8)
                receivedChecksum = receivedChecksum | received[index - 1]

                ## Deep DEBUG
                ## utilities.printDebug('Packet received checksum: ' + str(receivedChecksum))

                if ( receivedChecksum != checksum ):
                    return False

                result = (packetType, packetData)
                return result

        return False

    """
    "" Verifies password of the fingerprint sensor.
    ""
    "" @return tuple (integer [1 byte])
    """
    def verifyPassword(self):

        packetData = (
            FINGERPRINT_VERIFYPASSWORD,
            utilities.rightShift(self.__password, 24),
            utilities.rightShift(self.__password, 16),
            utilities.rightShift(self.__password, 8),
            utilities.rightShift(self.__password, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Sets the password of the fingerprint sensor.
    ""
    "" @param integer newPassword (4 bytes)
    "" @return tuple (integer [1 byte])
    """
    def setPassword(self, newPassword):

        ## Validates the password (maximum 4 bytes)
        if ( newPassword < 0x00000000 or newPassword > 0xFFFFFFFF ):
            raise ValueError('The given password is not valid!')

        packetData = (
            FINGERPRINT_SETPASSWORD,
            utilities.rightShift(newPassword, 24),
            utilities.rightShift(newPassword, 16),
            utilities.rightShift(newPassword, 8),
            utilities.rightShift(newPassword, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Sets the module address of the fingerprint sensor.
    ""
    "" @param integer newAddress (4 bytes)
    "" @return tuple (integer [1 byte])
    """
    def setAddress(self, newAddress):

        ## Validates the address (maximum 4 bytes)
        if ( newAddress < 0x00000000 or newAddress > 0xFFFFFFFF ):
            raise ValueError('The given address is not valid!')

        packetData = (
            FINGERPRINT_SETADDRESS,
            utilities.rightShift(newAddress, 24),
            utilities.rightShift(newAddress, 16),
            utilities.rightShift(newAddress, 8),
            utilities.rightShift(newAddress, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

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

        packetData = (
            FINGERPRINT_SETSYSTEMPARAMETER,
            parameterNumber,
            parameterValue,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Gets all system parameters of the fingerprint sensor.
    ""
    "" @return tuple (integer [17 bytes])
    """
    def getSystemParameters(self):

        packetData = (
            FINGERPRINT_GETSYSTEMPARAMETERS,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Gets the number of stored templates.
    ""
    "" @return tuple (integer [3 bytes])
    """
    def getTemplateCount(self):

        packetData = (
            FINGERPRINT_TEMPLATECOUNT,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Reads the characteristics of a finger.
    ""
    "" @return tuple (integer [1 byte])
    """
    def readImage(self):

        packetData = (
            FINGERPRINT_READIMAGE,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Converts the read finger characteristics and stores it temporarily in ImageBuffer1 or ImageBuffer2.
    ""
    "" @param integer bufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def convertImage(self, bufferNumber = 1):

        if ( bufferNumber != 1 and bufferNumber != 2 ):
            raise ValueError('The given buffer number is not valid!')

        packetData = (
            FINGERPRINT_CONVERTIMAGE,
            bufferNumber,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Compares the finger characteristics of ImageBuffer1 with ImageBuffer2 and returns the accuracy score.
    ""
    "" @return tuple (integer [3 bytes])
    """
    def compareImages(self):

        packetData = (
            FINGERPRINT_COMPAREIMAGES,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Downloads the finger characteristics of ImageBuffer1 or ImageBuffer2
    ""
    "" @param integer bufferNumber (1 byte)
    "" @return tuple (integer [3 bytes])
    """
    def downloadImage(self, bufferNumber = 1):

        if ( bufferNumber != 1 and bufferNumber != 2 ):
            raise ValueError('The given buffer number is not valid!')

        packetData = (
            FINGERPRINT_DOWNLOADIMAGE,
            bufferNumber,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)

        ## Gets first reply packet
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        """
        completePacketData = [

        ]


        ## Gets follow-up packet
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_DATAPACKET ):
            return (-1,)
        """

        return receivedPacketData















    """
    "" Combines the fingerprint characteristics temporarily stored in ImageBuffer1 and ImageBuffer2 to a template.
    "" The created template (the result) will be stored again in ImageBuffer1 and ImageBuffer2 as the same.
    ""
    "" @return tuple (integer [1 byte])
    """
    def createTemplate(self):

        packetData = (
            FINGERPRINT_CREATETEMPLATE,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Saves a template from the specified ImageBufferN (N = [1|2]) to the given position number.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @param integer bufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def storeTemplate(self, positionNumber, bufferNumber = 1):

        if ( bufferNumber != 1 and bufferNumber != 2 ):
            raise ValueError('The given buffer number is not valid!')

        packetData = (
            FINGERPRINT_STORETEMPLATE,
            bufferNumber,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Loads an existing template specified by position number to ImageBufferN (N = [1|2]).
    ""
    "" @param integer positionNumber (2 bytes)
    "" @param integer bufferNumber (1 byte)
    "" @return tuple (integer [1 byte])
    """
    def loadTemplate(self, positionNumber, bufferNumber = 1):

        if ( bufferNumber != 1 and bufferNumber != 2 ):
            raise ValueError('The given buffer number is not valid!')

        packetData = (
            FINGERPRINT_LOADTEMPLATE,
            bufferNumber,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Deletes one template from fingerprint database.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @return tuple (integer [1 byte])
    """
    def deleteTemplate(self, positionNumber):

        ## Delete only one template
        period = 0x0001

        packetData = (
            FINGERPRINT_DELETETEMPLATE,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
            utilities.rightShift(period, 8),
            utilities.rightShift(period, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Search if the readed image in ImageBufferN in database.
    ""
    "" @return tuple (integer [5 bytes])
    """
    def searchTemplate(self):

        ## ImageBuffer1 and ImageBuffer2 are the same in this case
        bufferNumber = 0x01

        ## Begin search at page 0x0000 for 0x00A3 (mean 163) templates
        positionStart = 0x0000
        templatesCount = 0x00A3

        packetData = (
            FINGERPRINT_SEARCHTEMPLATE,
            bufferNumber,
            utilities.rightShift(positionStart, 8),
            utilities.rightShift(positionStart, 0),
            utilities.rightShift(templatesCount, 8),
            utilities.rightShift(templatesCount, 0),
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData

    """
    "" Clears the complete template database.
    ""
    "" @return tuple (integer [1 byte])
    """
    def clearDatabase(self):

        packetData = (
            FINGERPRINT_CLEARDATABASE,
        )

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return (-1,)

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return (-1,)

        return receivedPacketData