#!/usr/bin/env python

## Enrolls new finger
##

import sys
import time

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

## Tries to enroll new finger
try:
    print 'Waiting for finger...'

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print 'Template already exists at position #' + str(positionNumber)
        exit(0)

    print 'Remove finger...'
    time.sleep(2)

    print 'Waiting for same finger again...'

    ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers and creates a template
    f.createTemplate()

    ## Gets new position number (the counting starts at 0, so we do not need to increment)
    positionNumber = f.getTemplateCount()

    ## Saves template at new position number
    if ( f.storeTemplate(positionNumber) == True ):
        print 'Finger enrolled successfully!'
        print 'New template position #' + str(positionNumber)

except:
    e = sys.exc_info()[1]
    print 'Fingerprint enroll failed!'
    print 'Exception message: ' + str(e.message)
    exit(1)