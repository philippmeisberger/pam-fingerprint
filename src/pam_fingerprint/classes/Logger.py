"""
"" PAM Fingerprint
"" Logger class.
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved.
"""

from pam_fingerprint.classes.Config import *
import time
import os


class Logger(object):

    """
    "" Log level constants
    "" @var integer
    """
    DEBUG = 0
    NOTICE = 1
    WARNING = 2
    ERROR = 3

    """
    "" The opened log file
    "" @var FileObject __file
    """
    __file = None

    """
    "" The config instance
    "" @var Config __config
    """
    __config = None
    
    """
    "" Constructor
    ""    
    "" @return void
    """
    def __init__(self):

        # Get path to log file
        self.__config = Config('/etc/pam_fingerprint.conf')
        logFile = self.__config.readString('Log', 'file')
        
        # Checks if path/file is writable
        if ( os.access(logFile, os.W_OK) == False ):
            raise Exception('The log file "' + logFile + '" is not writable!')

        # Opens log file for appending text 
        self.__file = open(logFile, 'a')

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        # Closes file if is open
        if (self.__file):
            self.__file.close()

    """
    "" Appends a string into the log file.
    ""
    "" @param integer level
    "" @param string caller
    "" @param string message
    "" @param boolean printMessage
    "" 
    "" @return void
    """
    def log(self, level, message):

        ## Gets logging level from configuration file
        loggingLevel = self.__config.readInteger('Log', 'level')
        
        if ( loggingLevel < 0 or loggingLevel > 3 ):
            raise Exception('Invalid configuration file (line "level" must be [0-3])!')

        ## Logs message only if level is greater than configured level
        if ( level >= loggingLevel ):           

            ## Gets log level label
            if (level == Logger.DEBUG):
                levelLabel = '[Debug]'
            elif (level == Logger.NOTICE):
                levelLabel = '[Notice]'
            elif (level == Logger.WARNING):
                levelLabel = '[Warning]'
            elif (level == Logger.ERROR):
                levelLabel = '[Error]'
            else:
                levelLabel = '[Unknown level]'

            ## Appends message to log
            self.__file.write(time.strftime('%Y-%m-%d %H:%M:%S: ') + levelLabel + ' ' + message + '\n')

            ## Prints all log messages which log level is greater than DEBUG
            if ( level >= Logger.DEBUG ):
                print levelLabel + ' pam_fingerprint: ' + message
