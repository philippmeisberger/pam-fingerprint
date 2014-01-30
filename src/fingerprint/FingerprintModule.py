"""
"" PAM Fingerprint
"" Fingerprint authentification module.
""
"" @author Bastian Raschke
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved.
"""

from utils.Logger import *
from utils.Config import *
from fingerprint.lib.Fingerprint import *
import fingerprint.lib.utilities as utilities
import time

class FingerprintModule(object):

    """
    "" The fingerprint library object
    "" @var Fingerprint __fingerprint
    """
    __fingerprint = None

    """
    "" Constructor
    ""
    "" @return void
    """
    def __init__(self):

        # Get connection values
        port = Config.getInstance().readString('FingerprintModule', 'port')
        baudRate = Config.getInstance().readInteger('FingerprintModule', 'baudRate')
        address = Config.getInstance().readHex('FingerprintModule', 'address')
        password = Config.getInstance().readHex('FingerprintModule', 'password')

        # Try to establish connection
        self.__fingerprint = Fingerprint(port, baudRate, address, password)

        p = self.__fingerprint.verifyPassword()

        if ( p[0] == FINGERPRINT_OK ):
            Logger.getInstance().log(Logger.DEBUG, __name__, 'Sensor password is correct.')
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            raise Exception('Communication error')           
        elif ( p[0] == FINGERPRINT_PASSFAIL ):
            raise Exception('Password is wrong')
        else:
            raise Exception('Unknown error')
            
    """
    "" Authenticates a user with a fingerprint.
    ""
    "" @return boolean
    """
    def authenticate(self):

        p = [-1]

        while ( p[0] != FINGERPRINT_OK ):

            # Get fingerprint image
            p = self.__fingerprint.getImage()

            if ( p[0] == FINGERPRINT_OK ):
                Logger.getInstance().log(Logger.DEBUG, __name__, 'Image taken.')
            elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
                Logger.getInstance().log(Logger.ERROR, __name__, 'Communication error')
            elif ( p[0] == FINGERPRINT_NOFINGER ):
                ## Will be logged many times
                Logger.getInstance().log(Logger.DEBUG, __name__, 'No finger found')
            elif ( p[0] == FINGERPRINT_IMAGEFAIL ):
                Logger.getInstance().log(Logger.ERROR, __name__, 'Imaging error')
            else:
                Logger.getInstance().log(Logger.ERROR, __name__, 'Unknown error')
                
            time.sleep(0.05)
        
        # First step is done
        p = self.__fingerprint.image2Tz(0x01);
        
        if ( p[0] == FINGERPRINT_OK ):
            Logger.getInstance().log(Logger.DEBUG, __name__, 'Image converted.')
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            Logger.getInstance().log(Logger.ERROR, __name__, 'Communication error')
            return False
        elif ( p[0] == FINGERPRINT_IMAGEMESS ):
            Logger.getInstance().log(Logger.ERROR, __name__, 'Image too messy!')
            return False
        elif ( p[0] == FINGERPRINT_FEATUREFAIL ):
            Logger.getInstance().log(Logger.ERROR, __name__, 'Could not find fingerprint features')
            return False
        elif ( p[0] == FINGERPRINT_INVALIDIMAGE ):
            Logger.getInstance().log(Logger.ERROR, __name__, 'Could not find fingerprint features')
            return False
        else:
            Logger.getInstance().log(Logger.ERROR, __name__, 'Unknown error')
            return False

        # Search fingerprint in database
        p = self.__fingerprint.searchTemplate();

        if ( p[0] == FINGERPRINT_OK ):
            Logger.getInstance().log(Logger.DEBUG, __name__, 'Found a match.')
        elif ( p[0] == FINGERPRINT_PACKETRECIEVEERR ):
            Logger.getInstance().log(Logger.ERROR, __name__, 'Communication error')
            return False
        elif ( p[0] == FINGERPRINT_NOTFOUND ):
            Logger.getInstance().log(Logger.DEBUG, __name__, 'Did not found a match')
            return False
        else:
            Logger.getInstance().log(Logger.ERROR, __name__, 'Unknown error')
            return False

        positionNumber = p[1]
        positionNumber = utilities.leftShift(positionNumber, 8)
        positionNumber = positionNumber | p[2]

        # TODO: Check if user exists in a file

        return True
