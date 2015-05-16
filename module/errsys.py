__author__ = 'yufeng'

import logging

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s  %(message)s')
logger.BASIC = logging.WARN
logger.DETAIL = logging.INFO
logger.level = logger.DETAIL