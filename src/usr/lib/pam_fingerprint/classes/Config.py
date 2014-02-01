"""
"" PAM Fingerprint
"" Configuration file class.
"" @see http://docs.python.org/3/library/configparser.html
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved.
"""

import ConfigParser
import os
import sys


class Config(object):

    """
    "" Singleton instance
    "" @var object __instance
    """
    __instance = None
    
    """
    "" The ConfigParser object
    "" @var ConfigParser __configParser
    """
    __configParser = None

    """
    "" Singleton method
    ""
    "" @return Config
    """
    @classmethod
    def getInstance(self):

        if (not self.__instance):
            self.__instance = Config(self.__configFile)
        return self.__instance
        
    """
    "" Constructor
    ""
    "" @param string configFile
    "" @return void
    """
    def __init__(self, configFile):

        self.__configFile = configFile
        
        # Checks if path/file is readable
        if ( os.access(configFile, os.R_OK) == False ):
            raise Exception('The configuration file \"' + configFile + '\" is not readable!')

        self.__configParser = ConfigParser.ConfigParser()
        self.__configParser.read(configFile)

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        # Saves config file
        self.__configParser.write(open(self.__configFile, 'w'))

    """
    "" Removes data from config file.
    ""
    "" @param string section
    "" @param string name
    "" @return boolean
    """
    def remove(self, section, name):

        return self.__configParser.remove_option(section, name)

    """
    "" Writes data into config file.
    ""
    "" @param string section
    "" @param string name
    "" @parama string value
    "" @return void
    """
    def writeString(self, section, name, value):

        self.__configParser.set(section, name, value)
        
    """
    "" Reads a string value from config file.
    ""
    "" @param string section
    "" @param string name
    "" @return string
    """
    def readString(self, section, name):

        return self.__configParser.get(section, name)

    """
    "" Reads a boolean value from config file.
    ""
    "" @param string section
    "" @param string name
    "" @return boolean
    """
    def readBoolean(self, section, name):

        return self.__configParser.getboolean(section, name)

    """
    "" Reads an integer value from config file.
    ""
    "" @param string section
    "" @param string name
    "" @return integer
    """
    def readInteger(self, section, name):

        ## Casts to integer (base 10)
        return int(self.readString(section, name), 10)

    """
    "" Reads a byte from config file.
    ""
    "" @param string section
    "" @param string name
    "" @return byte
    """
    def readHex(self, section, name):

        ## Casts to integer (base 16)
        return int(self.readString(section, name), 16)

    """
    "" Checks if a section exists.
    ""
    "" @param string name
    "" @return boolean
    """
    def sectionExists(self, name):
    
        return (name in self.__configParser)

    """
    "" Returns all sections as an array.
    ""
    "" @return array
    """
    def getSections(self):
    
        return self.__configParser.sections()

    """
    "" Returns all items of a sections as an array.
    ""
    "" @return array
    """
    def getItems(self, section):

        return self.__configParser.items(section)
