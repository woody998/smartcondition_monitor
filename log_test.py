import logging
import logging.handlers
import configparser
import os.path
import datetime

config = configparser.ConfigParser()
config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'default.cfg'))
config.read(config_file_path)

logger = logging.getLogger('logger')
logger.setLevel(level = logging.DEBUG)
rf_handler = logging.handlers.TimedRotatingFileHandler('all.log', when = 'midnight', interval = 1, backupCount = 7, atTime = datetime.time(0,0,0,0))
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

f_handler = logging.FileHandler('error.log')
f_handler.setLevel(logging.ERROR)
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)

lon = 100
lat = 1000

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')

logger.debug('lon:%d; lat:%d',lon,lat)