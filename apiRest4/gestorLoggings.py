import logging
import logging.handlers

LOG_FILENAME = 'loggings.log'

# create logger
logger = logging.getLogger("Montura")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
h = logging.handlers.RotatingFileHandler(LOG_FILENAME, 'a', maxBytes=1024*1024, backupCount=5)
f = logging.Formatter('%(levelname)-8s %(asctime)s-10s %(name)s %(message)s')
h.setFormatter(f)
logger.addHandler(h)

def anadirAlLog(mensaje, tipo):
    if tipo == 'INFO':
        logger.info(mensaje)
    elif tipo == 'ERROR':
        logger.error(mensaje)
