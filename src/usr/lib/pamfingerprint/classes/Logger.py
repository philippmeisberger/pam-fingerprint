import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Creates and adds an output handler
strmHandler = logging.StreamHandler()
strmHandler.setLevel(logging.DEBUG)
strmHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(strmHandler)
