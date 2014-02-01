"""
"" PyFingerprint
"" A python written library for an UART optical fingerprint sensor.
""
"" Requirements:
"" ~# apt-get install python-pip
"" ~# pip install pyserial
""
"" Inspired by Adafruit Industries
"" @see https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library
""
"" Additionally:
"" @see http://pyserial.sourceforge.net
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved.
""
"""

from includes.constants import *
import includes.utilities

import serial
import struct
import os.path


class Fingerprint(object):

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
    "" @var Serial __uart
    """
    __uart = None

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

        if ( os.path.exists(port) == False ):
            raise Exception('No valid fingerprint sensor port found!')

        self.__address = address
        self.__password = password

        ## Initializes connection
        self.__uart = serial.Serial(port, baudRate, serial.EIGHTBITS)

        ## Sets timeout
        ## self.__uart.timeout = 2

        ## Re-opens connection
        self.__uart.close()
        self.__uart.open()

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        ## Closes connection if established
        if (self.__uart):
            self.__uart.close()

    """
    "" Sends a packet to fingerprint sensor.
    ""
    "" @param integer address (4 bytes)
    "" @param integer packetType (1 byte)
    "" @param integer length (2 byte)
    "" @param array<integer> packetData
    "" @return boolean
    """
    def writePacket(self, address, packetType, length, packetData):

        ## Writes header (one byte at once)
        self.__uart.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__uart.write(utilities.byteToString(utilities.rightShift(address, 24)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(address, 16)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(address, 8)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(address, 0)))

        self.__uart.write(utilities.byteToString(packetType))

        self.__uart.write(utilities.byteToString(utilities.rightShift(length, 8)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(length, 0)))

        ## Calculates checksum:
        ## checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
        checksum = packetType + utilities.rightShift(length, 8) + utilities.rightShift(length, 0)

        ## Writes payload
        for i in range(0, len(packetData)):

            self.__uart.write(utilities.byteToString(packetData[i]))
            checksum += packetData[i]

        ## Writes checksum (2 bytes)
        self.__uart.write(utilities.byteToString(utilities.rightShift(checksum, 8)))
        self.__uart.write(utilities.byteToString(utilities.rightShift(checksum, 0)))

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

            ## Tries to read one byte
            read = self.__uart.read()

            if ( len(read) != 0 ):

                ## DEBUG
                ## print 'Received packet fragment ' + str(index) + ' = '+ str(struct.unpack('@c', read)[0])
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

                    ## DEBUG
                    ## print 'Packet is corrupted (FINGERPRINT_STARTCODE not found)!'
                    break ## Returns false at end

                ## Calculates length of the 2 length bytes
                length = received[7]
                length = utilities.leftShift(length, 8)
                length = length | received[8]

                ## Subtracts 2 bytes of packet (checksum)
                length = length - 2

                ## Continue to next loop if the packet is still not fully received
                if ( index <= length + 10 ):
                    continue

                ## DEBUG
                ## print 'Packet length: ' + str(length)

                packetType = received[6]

                ## Calculates checksum:
                ## checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
                checksum = packetType + received[7] + received[8]

                packetData = []

                ## Build package payload
                for i in range(9, length + 9):
                    packetData.append(received[i])
                    checksum += received[i]

                ## DEBUG
                ## print 'Packet calculated checksum: ' + str(checksum)

                ## Calculates full checksum of the 2 separate checksum bytes
                receivedChecksum = received[index - 2]
                receivedChecksum = utilities.leftShift(receivedChecksum, 8)
                receivedChecksum = receivedChecksum | received[index - 1]

                ## DEBUG
                ## print 'Packet received checksum: ' + str(receivedChecksum)

                if ( receivedChecksum != checksum ):

                    ## DEBUG
                    ## print 'Packet checksum is not correct!'
                    break ## Returns false at end

                result = (packetType, packetData)
                return result

        return False

    """
    "" Verifies password of the fingerprint sensor.
    ""
    "" @return integer (1 byte)
    """
    def verifyPassword(self):

        packetData = [
            FINGERPRINT_VERIFYPASSWORD,
            utilities.rightShift(self.__password, 24),
            utilities.rightShift(self.__password, 16),
            utilities.rightShift(self.__password, 8),
            utilities.rightShift(self.__password, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return False

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Sets the password of the fingerprint sensor.
    ""
    "" @param integer newPassword (4 bytes)
    "" @return integer (1 byte)
    """
    def setPassword(self, newPassword):

        packetData = [
            FINGERPRINT_SETPASSWORD,
            utilities.rightShift(newPassword, 24),
            utilities.rightShift(newPassword, 16),
            utilities.rightShift(newPassword, 8),
            utilities.rightShift(newPassword, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return False

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Sets the module address of the fingerprint sensor.
    ""
    "" @param integer newAddress (4 bytes)
    "" @return integer (1 byte)
    """
    def setAddress(self, newAddress):

        packetData = [
            FINGERPRINT_SETADDRESS,
            utilities.rightShift(newAddress, 24),
            utilities.rightShift(newAddress, 16),
            utilities.rightShift(newAddress, 8),
            utilities.rightShift(newAddress, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return False

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Gets the number of stored templates.
    ""
    "" @return integer (2 bytes)
    """
    def getTemplateCount(self):

        packetData = [
            FINGERPRINT_TEMPLATECOUNT
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Reads the image of a finger.
    ""
    "" @return integer (1 byte)
    """
    def getImage(self):

        packetData = [
            FINGERPRINT_GETIMAGE
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Generates fingerprint characteristics of readed image and stores temporaryly in ImageBuffer1 or ImageBuffer2.
    ""
    "" @param integer bufferNumber (1 byte)
    "" @return integer (1 byte)
    """
    def image2Tz(self, bufferNumber = 0x01):

        packetData = [
            FINGERPRINT_IMAGE2TZ,
            bufferNumber 
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Combines fingerprint characteristics of ImageBuffer1 with ImageBuffer2 to a template.
    ""
    "" @return integer (1 byte)
    """
    def createTemplate(self):

        packetData = [
            FINGERPRINT_REGMODEL
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Saves the template of ImageBufferN on a specific position number.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @return integer (1 byte)
    """
    def storeTemplate(self, positionNumber):

        bufferNumber = 0x01

        packetData = [
            FINGERPRINT_STORE,
            bufferNumber,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Deletes one template from fingerprint database.
    ""
    "" @param integer positionNumber (2 bytes)
    "" @return integer (1 byte)
    """
    def deleteTemplate(self, positionNumber):

        period = 0x0001
        
        packetData = [
            FINGERPRINT_DELETECHAR,
            utilities.rightShift(positionNumber, 8),
            utilities.rightShift(positionNumber, 0),
            utilities.rightShift(period, 8),
            utilities.rightShift(period, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Clears the complete template database.
    ""
    "" @return integer (1 byte)
    """
    def clearDatabase(self):

        packetData = [
            FINGERPRINT_EMPTY
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData

    """
    "" Search if the readed image in ImageBufferN in database.
    ""
    "" @return integer (5 bytes)
    """
    def searchTemplate(self):

        ## ImageBuffer1 and ImageBuffer2 are the same in this case
        bufferNumber = 0x01

        ## Begin search at page 0x0000 for 0x00A3 (=163) templates
        positionStart = 0x0000
        templatesCount = 0x00A3

        packetData = [
            FINGERPRINT_SEARCH,
            bufferNumber,
            utilities.rightShift(positionStart, 8),
            utilities.rightShift(positionStart, 0),
            utilities.rightShift(templatesCount, 8),
            utilities.rightShift(templatesCount, 0)
        ]

        self.writePacket(self.__address, FINGERPRINT_COMMANDPACKET, len(packetData) + 2, packetData)
        receivedPacket = self.readPacket()

        if ( receivedPacket == False ):
            return -1

        receivedPacketType = receivedPacket[0]
        receivedPacketData = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            return -1

        return receivedPacketData
