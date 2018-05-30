import logging
import sys
import time


def init_logging(prefix, level="INFO"):
    # Init rules
    logger = logging.getLogger()
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    log_file = sys.path[0] + "/logs/" + prefix + "-" + timestamp + ".log"
    formatter = "[%(asctime)s] [%(threadName)s] [%(levelname)s] %(message)s"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    # Apply the rules and add stdout logger
    logging.basicConfig(level=level, format=formatter)
    fh.setFormatter(logging.Formatter(formatter))
    logger.addHandler(fh)
