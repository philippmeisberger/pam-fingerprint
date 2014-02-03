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

import includes.utilities as utilities
from includes.constants import *

from PyFingerprintConnection import *


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
        p = self.__connection.verifyPassword()

        if ( p[0] == FINGERPRINT_OK ):
            utilities.printDebug('Sensor password is correct')

        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')

        elif ( p[0] == FINGERPRINT_PASSFAIL ):
            raise Exception('Sensor password is wrong')

        else:
            raise Exception('Unknown error')

    """
    "" Scans a finger.
    ""
    "" @return tuple (boolean, integer)
    """
    def checkFingerprint(self):

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

    # TODO: maybe we need a fingerprint storing method
    """
    def addFingerprint(self):
        
    """
