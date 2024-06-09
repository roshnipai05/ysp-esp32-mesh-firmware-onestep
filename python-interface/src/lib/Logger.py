import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class ColorizedLoggingHandler(logging.StreamHandler):
    colors = {
        'INFO': Fore.BLUE + Style.NORMAL,
        'WARNING': Fore.YELLOW + Style.NORMAL,
        'ERROR': Fore.RED + Style.NORMAL,
        'DEBUG': Fore.WHITE + Style.NORMAL,
    }

    def emit(self, record):
        try:
            msg = self.format(record)
            levelname = record.levelname
            color = self.colors.get(levelname, Fore.WHITE)
            stream = self.stream
            stream.write(color + msg + colorama.Style.RESET_ALL + '\n')
            stream.flush()
        except Exception:
            self.handleError(record)

def get_logger(name='ColorLogger', level = logging.DEBUG):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)  # Set the default log level
        ch = ColorizedLoggingHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        if level == logging.DEBUG:
            formatter = logging.Formatter('%(levelname)s: [%(funcName)s:%(lineno)d] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def pprint(message, end='\n'):
    print(Fore.CYAN + message + Style.RESET_ALL, end=end)

class ControlFlowException(Exception):
    """
    Raised when we encounter unexpected control flow in user-facing sections
    """
    pass

