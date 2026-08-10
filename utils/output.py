import sys
import logging


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[90m",
        logging.INFO: "\033[95m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[91m",
    }
    PREFIXES = {
        logging.DEBUG: "[D] ",
        logging.INFO: "[*] ",
        logging.WARNING: "[!] ",
        logging.ERROR: "[!] ",
        logging.CRITICAL: "[!] ",
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        prefix = self.PREFIXES.get(record.levelno, "")
        msg = record.getMessage()
        return f"{color}{prefix}{msg}{self.RESET}"


def setup_logger(name: str = "webinfo", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColorFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


log = setup_logger()
