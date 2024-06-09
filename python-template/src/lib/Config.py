import logging
import os
import sys

from Logger import get_logger, pprint

LIB_DIR = os.path.dirname( os.path.abspath(__file__) )
SRC_DIR = os.path.dirname(LIB_DIR)

if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

TOPOLOGY_FILE = os.path.join(SRC_DIR, 'topology.json')
WORDLIST_FILE = os.path.join(LIB_DIR, 'wordlist')
EXIT_COMMAND = 'exit'
SOCK_HOST = '127.0.0.1'
SOCK_PORT = 65432

# set the log level here
LOG_LEVEL = logging.INFO

log = get_logger(level = LOG_LEVEL)

