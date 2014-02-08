## see http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Creates and adds an output handler
strmHandler = logging.StreamHandler()
strmHandler.setLevel(logging.DEBUG)
strmHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(strmHandler)

# Creates and adds a file handler
fileHandler = logging.FileHandler('/var/log/pamfingerprint.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(fileHandler)





logger.info('Hello baby')