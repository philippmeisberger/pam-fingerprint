"""
"" PAM Fingerprint
"" A python written library for Adafruit optical fingerprint sensor.
""
"" @author Bastian Raschke
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved.
"""

import struct


"""
"" Shifts a byte.
""
"" @param byte byte (n byte)
"" @param integer x
"" @return byte
"""
def rightShift(byte, x):
  return (byte >> x & 0xFF)

"""
"" Shifts a byte.
""
"" @param byte byte (n byte)
"" @param integer x
"" @return byte
"""
def leftShift(byte, x):
  return (byte << x)

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
