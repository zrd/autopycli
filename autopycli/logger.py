import logging
import logging.config
import sys


logger = logging.getLogger(__name__)
stoh = logging.StreamHandler(sys.stdout)
fmth = logging.Formatter("[%(levelname)s] %(asctime)s %(message)s")
stoh.setFormatter(fmth)
logger.addHandler(stoh)
logger.setLevel("DEBUG")
