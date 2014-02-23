"""
"" PyFingerprint
""
"" Copyright 2014 Bastian Raschke.
"" All rights reserved.
"""

import struct


"""
"" Shifts a byte.
""
"" @param integer n
"" @param integer x
"" @return integer
"""
def rightShift(n, x):

    return (n >> x & 0xFF)

"""
"" Shifts a byte.
""
"" @param integer n
"" @param integer x
"" @return integer
"""
def leftShift(n, x):

    return (n << x)

"""
"" Gets the bit at place p of number n.
""
"" @param integer n
"" @param integer p
"" @return integer
"""
def bitAtPosition(n, p):

    ## A bitshift 2 ^ p
    twoP = 1 << p

    ## Binary AND composition (on both position must be a 1)
    ## This can only happen at position p
    result = n & twoP
    return int(result > 0)

"""
"" Converts a byte to string.
""
"" @param byte byte
"" @return string
"""
def byteToString(byte):

    return struct.pack('@B', byte)

"""
"" Converts one "string" byte (like '0xFF') to real byte (0xFF).
""
"" @param string string
"" @return byte
"""
def stringToByte(string):

    tupel = struct.unpack('@B', string)
    return tupel[0]