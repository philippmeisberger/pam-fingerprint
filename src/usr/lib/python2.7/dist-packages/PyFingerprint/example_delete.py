## Deletes a finger from sensor
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

## Tries to delete the template of the finger
try:
    positionNumber = raw_input('Please enter the template position you want to delete: ')
    positionNumber = int(positionNumber)

    if ( f.deleteTemplate(positionNumber) == True ):
        print 'Template deleted!'

except Exception as e:
    print 'Delete template failed!'
    print 'Exception: ' + e.message
    exit(1)