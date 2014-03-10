#!/usr/bin/env python

## Search for a finger
##

import hashlib
import sys

from PyFingerprint import *

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except:
    e = sys.exc_info()[1]
    print 'The fingerprint sensor could not be initialized!'
    print 'Exception message: ' + str(e.message)
    exit(1)

## Gets some sensor information
print 'Currently stored templates: ' + str(f.getTemplateCount())

## Tries to search the finger and calculate hash
try:
    print 'Waiting for finger...'

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Searchs template
    result = f.searchTemplate()
    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print 'No match found!'
        exit(0)
    else:
        print 'Found template at position #' + str(positionNumber)
        print 'The accuracy score is: ' + str(accuracyScore)

    ## OPTIONAL stuff
    ##

    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in charbuffer 1
    characterics = f.downloadCharacteristics(0x01)

    ## Hashes characteristics of template
    print 'SHA2 hash of template: ' + hashlib.sha256(str(characterics)).hexdigest()

except:
    e = sys.exc_info()[1]
    print 'Fingerprint read failed!'
    print 'Exception message: ' + str(e.message)
    exit(1)