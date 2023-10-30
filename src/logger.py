import logging


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter class that adds color to log messages.
    """

    COLOR_CODES = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[1;41m',  # White on red background
    }

    def format(self, record):
        """
        Format the log message with color.

        :param record: The log record to format.
        :type record: LogRecord
        :return: The formatted log message with color.
        :rtype: str
        """
        log_message = super().format(record)
        return f"{self.COLOR_CODES[record.levelname]}{log_message}\033[0m"


def setup_logging(level=logging.INFO):
    """
    Set up colored logging.

    This function configures colored logging using the ColoredFormatter class.

    :param level: The logging level.
    :type level: int
    :return: The configured logger instance.
    :rtype: Logger
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
