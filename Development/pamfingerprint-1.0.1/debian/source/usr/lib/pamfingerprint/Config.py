"""
"" pamfingerprint
"" Configuration file management.
"" 
"" Copyright 2014 Philipp Meisberger, Bastian Raschke.
"" All rights reserved.
"""

## Documentation: @see http://docs.python.org/3/library/configparser.html
import ConfigParser
import os


class Config(object):

    """
    "" The config file path.
    "" @var string
    """
    __configFile = None

    """
    "" Flag that indicates config file will be not modified.
    "" @var boolean
    """
    __readOnly = False

    """
    "" The ConfigParser instance.
    "" @var ConfigParser
    """
    __configParser = None
    
    """
    "" Constructor
    ""
    "" @param string configFile
    "" @param boolean readOnly
    "" @return void
    """
    def __init__(self, configFile, readOnly = False):

        # Checks if path/file is readable
        if ( os.access(configFile, os.R_OK) == False ):
            raise Exception('The configuration file "' + configFile + '" is not readable!')

        self.__configFile = configFile
        self.__readOnly = readOnly

        self.__configParser = ConfigParser.ConfigParser()
        self.__configParser.read(configFile)

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        self.save()

    """
    "" Writes modifications to config file.
    ""
    "" @return boolean
    """
    def save(self):

        if ( self.__readOnly == True ):
            return False

        # Checks if path/file is writable
        if ( os.access(self.__configFile, os.W_OK) == True ):

            f = open(self.__configFile, 'w')
            self.__configParser.write(f)
            f.close()

            return True

        return False

    """
    "" Reads a string value.
    ""
    "" @param string section
    "" @param string name
    "" @return string
    """
    def readString(self, section, name):

        return self.__configParser.get(section, name)

    """
    "" Writes a string value.
    ""
    "" @param string section
    "" @param string name
    "" @param string value
    "" @return void
    """
    def writeString(self, section, name, value):

        self.__configParser.set(section, name, value)

    """
    "" Reads a boolean value.
    ""
    "" @param string section
    "" @param string name
    "" @return boolean
    """
    def readBoolean(self, section, name):

        return self.__configParser.getboolean(section, name)

    """
    "" Reads a decimal integer value.
    ""
    "" @param string section
    "" @param string name
    "" @return integer
    """
    def readInteger(self, section, name):

        ## Casts to integer (base 10)
        return int(self.readString(section, name), 10)

    """
    "" Reads a hexadecimal integer value.
    ""
    "" @param string section
    "" @param string name
    "" @return integer
    """
    def readHex(self, section, name):

        ## Casts to integer (base 16)
        return int(self.readString(section, name), 16)

    """
    "" Reads a list.
    ""
    "" @param string section
    "" @param string name
    "" @return list
    """
    def readList(self, section, name):

        unpackedList = self.readString(section, name)
        return unpackedList.split(',')

    """
    "" Writes a list.
    ""
    "" @param string section
    "" @param string name
    "" @param list value
    "" @return void
    """
    def writeList(self, section, name, value):

        delimiter = ','
        self.__configParser.set(section, name, delimiter.join(value))

    """
    "" Removes a value.
    ""
    "" @param string section
    "" @param string name
    "" @return boolean
    """
    def remove(self, section, name):

        return self.__configParser.remove_option(section, name)

    """
    "" Checks if a given section exists.
    ""
    "" @param string section
    "" @return boolean
    """
    def sectionExists(self, section):

        return self.__configParser.has_section(section)

    """
    "" Checks if an item in a given section exists.
    ""
    "" @param string section
    "" @param string name
    "" @return boolean
    """
    def itemExists(self, section, name):

        return self.__configParser.has_option(section, name)

    """
    "" Returns all sections as a list.
    ""
    "" @return list
    """
    def getSections(self):

        return self.__configParser.sections()

    """
    "" Returns all items of a sections as a list.
    ""
    "" @return list
    """
    def getItems(self, section):

        return self.__configParser.items(section)
