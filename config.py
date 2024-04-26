import logging as liblogging
from logging.handlers import RotatingFileHandler

DATABASE_FILE_NAME = 'thethirstydrifter_marketing.db'

DEFAULT_DELAY_SECONDS = 3



LOG_FILENAME = 'thethirstydrifter_marketing.log'
LOG_LEVEL = liblogging.INFO

logging = liblogging.getLogger('MarkingLogger')
def do_logging():
    logging.setLevel(LOG_LEVEL)
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=10)
    formatter = liblogging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.addHandler(handler)
    liblogging.basicConfig(level=liblogging.INFO)
do_logging()
