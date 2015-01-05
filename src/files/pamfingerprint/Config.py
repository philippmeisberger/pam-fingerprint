#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PAM Fingerprint

Copyright 2014 Philipp Meisberger, Bastian Raschke.
All rights reserved.
"""

## Documentation: @see http://docs.python.org/3/library/configparser.html
import ConfigParser
import os


class Config(object):
    """
    Configuration file management.

    The config file path.
    @var string

    Flag that indicates config file will be not modified.
    @var boolean

    The ConfigParser instance.
    @var ConfigParser
    """
    __configFile = None
    __readOnly = False
    __configParser = None

    def __init__(self, configFile, readOnly = False):
        """
        Constructor

        @param string configFile
        @param boolean readOnly
        """

        # Checks if path/file is readable
        if ( os.access(configFile, os.R_OK) == False ):
            raise Exception('The configuration file "' + configFile + '" is not readable!')

        self.__configFile = configFile
        self.__readOnly = readOnly

        self.__configParser = ConfigParser.ConfigParser()
        self.__configParser.read(configFile)

    def __del__(self):
        """
        Destructor

        """

        self.save()

    def save(self):
        """
        Writes modifications to config file.

        @return boolean
        """

        if ( self.__readOnly == True ):
            return False

        # Checks if path/file is writable
        if ( os.access(self.__configFile, os.W_OK) == True ):

            f = open(self.__configFile, 'w')
            self.__configParser.write(f)
            f.close()

            return True

        return False

    def readString(self, section, name):
        """
        Reads a string value.

        @param string section
        @param string name
        @return string
        """

        return self.__configParser.get(section, name)

    def writeString(self, section, name, value):
        """
        Writes a string value.

        @param string section
        @param string name
        @param string value
        @return void
        """

        self.__configParser.set(section, name, value)

    def readBoolean(self, section, name):
        """
        Reads a boolean value.

        @param string section
        @param string name
        @return boolean
        """

        return self.__configParser.getboolean(section, name)

    def readInteger(self, section, name):
        """
        Reads a decimal integer value.

        @param string section
        @param string name
        @return integer
        """

        ## Casts to integer (base 10)
        return int(self.readString(section, name), 10)

    def readHex(self, section, name):
        """
        Reads a hexadecimal integer value.

        @param string section
        @param string name
        @return integer
        """

        ## Casts to integer (base 16)
        return int(self.readString(section, name), 16)

    def readList(self, section, name):
        """
        Reads a list.

        @param string section
        @param string name
        @return list
        """

        unpackedList = self.readString(section, name)
        return unpackedList.split(',')

    def writeList(self, section, name, value):
        """
        Writes a list.

        @param string section
        @param string name
        @param list value
        @return void
        """

        delimiter = ','
        self.__configParser.set(section, name, delimiter.join(value))

    def remove(self, section, name):
        """
        Removes a value.

        @param string section
        @param string name
        @return boolean
        """

        return self.__configParser.remove_option(section, name)

    def sectionExists(self, section):
        """
        Checks if a given section exists.

        @param string section
        @return boolean
        """

        return self.__configParser.has_section(section)

    def itemExists(self, section, name):
        """
        Checks if an item in a given section exists.

        @param string section
        @param string name
        @return boolean
        """

        return self.__configParser.has_option(section, name)

    def getSections(self):
        """
        Returns all sections as a list.

        @return list
        """

        return self.__configParser.sections()

    def getItems(self, section):
        """
        Returns all items of a sections as a list.

        @return list
        """

        return self.__configParser.items(section)
