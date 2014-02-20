## Search for a finger
##

import time
import hashlib

from PyFingerprint import *

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except (Exception, ValueError) as e:
    print 'The fingerprint sensor could not be initialized!'
    print 'Exception: ' + e.message
    exit(1)

## Gets some sensor information
print 'Currently stored templates: ' + str(f.getTemplateCount())

## Tries to search the finger and calculate hash
try:
    print 'Waiting for finger...'

    while ( f.readImage() == False ):
        pass

    f.convertImage(0x01)

    result = f.searchTemplate()
    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber > 0 ):
        print 'Found template #' + str(positionNumber)
        print 'The accuracy score is: ' + str(accuracyScore)
    else:
        print 'No match found!'
        exit(0)

    ## Loads the found template to char buffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in char buffer 1
    characterics = f.downloadCharacteristics(0x01)

    ## Hashes characteristics of template
    print 'SHA2 hash: ' + hashlib.sha256(str(characterics)).hexdigest()

except Exception as e:
    print 'Fingerprint read failed!'
    print 'Exception: ' + e.message
    exit(1)