#!/usr/bin/env python

from Config import *

## Tries to init config instance
try:
    __config = Config('test.conf')

except Exception as e:
    print '[Exception] ' + e.message
    exit(1)

userName = 'phil1'
"""
## Tries to get fingerprint hash of user
try:
    ## Checks if user exists
    if ( __config.itemExists('Users', userName) ):

        ## Gets user authentication tuple (position, hash)
        userData = __config.readList('Users', userName)

        if ( len(userData) != 2 ):
            raise ValueError('Invalid tuple: Missing position or hash!')
            
        positionNumber = userData[0]
        expectedFingerprintHash = userData[1]
    else:
        raise ValueError('The user "' + userName + '" does not exist!')

    print str(positionNumber)
    print expectedFingerprintHash
    
except ValueError as e:
    print '[Exception] ' + e.message
"""
## write list

dataTuple = []
freePositionNumber = 0
fingerprintHash = '83dafe6c587234421a9b86987a4baf5a93aa1c531e34d364ea74f7e282b5b2a2'

dataTuple.append(str(freePositionNumber))
dataTuple.append(fingerprintHash)

__config.writeList('Users', userName, dataTuple)
#__config.writeList('Users', userName, dataTuple)

if ( __config.save() == True ):
    print 'The user "' + userName + '" has been added successfully!'
else:
    raise Exception('The configuration could not be written!')
