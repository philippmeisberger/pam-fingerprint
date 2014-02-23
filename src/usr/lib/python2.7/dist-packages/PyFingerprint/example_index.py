## Shows the template index table
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

## Tries to show a template index table page
try:
    page = raw_input('Please enter the index page (0, 1, 2, 3) you want to see: ')
    page = int(page)

    tableIndex = f.getTemplateIndex(page)

    for i in range(0, len(tableIndex)):
        print 'Template at position #' + str(i) + ' is used: ' + str(tableIndex[i])

except Exception as e:
    print 'Read out table index failed!'
    print 'Exception: ' + e.message
    exit(1)