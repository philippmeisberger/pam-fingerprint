## Enrolls new finger
##

import time

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

## Tries to enroll new finger
try:
    print 'Waiting for finger...'

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts image to characteristics and stores it in char buffer 1
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

    while ( f.readImage() == False ):
        pass

    ## Converts image to characteristics and stores it in char buffer 2
    f.convertImage(0x02)

    ## Compares the char buffers and creates a template
    f.createTemplate()

    ## Gets new position number
    positionNumber = f.getTemplateCount()
    positionNumber = positionNumber + 1

    ## Saves template at new position number
    if ( f.storeTemplate(positionNumber) == True ):
        print 'Finger enrolled successfully!'
        print 'New position number #' + str(positionNumber)

except Exception as e:
    print 'Fingerprint enroll failed!'
    print 'Exception: ' + e.message
    exit(1)