import logging
import sys

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(
	logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

logger = logging.getLogger("backboard-logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.propagate = False

