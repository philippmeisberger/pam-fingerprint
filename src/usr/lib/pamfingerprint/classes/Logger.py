"""
"" PAM Fingerprint
"" Lightweight system logger.
""
"" Copyright 2014 Philipp Meisberger, Bastian Raschke.
"" All rights reserved.
"""

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
    "" The file instance
    "" @var FileObject __file
    """
    __file = None

    """
    "" Logging level
    "" @var integer __logLevel
    """
    __logLevel = None

    """
    "" PAM handle
    "" @var handle __pamh
    """
    __pamh = None
    
    """
    "" Constructor
    ""
    "" @param string logFile
    "" @param integer logLevel
    "" @return void
    """
    def __init__(self, logFile, logLevel, pamhandle=None):

        ## Checks if path/file is writable
        if ( os.access(logFile, os.W_OK) == False ):
            raise Exception('The log file "' + logFile + '" is not writable!')

        if ( logLevel < 0 or logLevel > 3 ):
            raise Exception('The log level must between 0 and 3!')

        ## Opens log file for appending text 
        self.__file = open(logFile, 'a')

        self.__logLevel = logLevel
        self.__pamh = pamhandle

    """
    "" Destructor
    ""
    "" @return void
    """
    def __del__(self):

        ## Closes file if is open
        if ( self.__file ):
            self.__file.close()

    """
    "" Appends a string into the log file.
    ""
    "" @param integer level
    "" @param string message
    "" 
    "" @return void
    """
    def log(self, level, message):

        ## Logs message only if level is greater than configured level
        if ( level >= self.__logLevel ):           

            ## Gets log level label
            if (level == self.DEBUG):
                levelLabel = '[Debug]'
            elif (level == self.NOTICE):
                levelLabel = '[Notice]'
            elif (level == self.WARNING):
                levelLabel = '[Warning]'
            elif (level == self.ERROR):
                levelLabel = '[Error]' 
            else:
                levelLabel = '[Unknown level]'

            ## Appends message to log and prints it
            self.__file.write(time.strftime('%Y-%m-%d %H:%M:%S ') + levelLabel +' '+ message +'\n')
            
            if ( self.__pamh == None ):
                ## Normal print
                print levelLabel + ' ' + message
            else:
                ## Use PAM library function
                if (level == self.ERROR):
                    pamMsgStyle = self.__pamh.PAM_ERROR_MSG
                else:
                    pamMsgStyle = self.__pamh.PAM_TEXT_INFO

                ## TODO: Add levelLabel to message???
                msg = self.__pamh.Message(pamMsgStyle, message)
                self.__pamh.conversation(msg)
