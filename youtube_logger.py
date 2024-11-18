import logging
from enum import Enum


class YoutubeLogger(logging.Logger):
    class Level(Enum):
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR

    def __init__(self, file_path: str, file_name: str, log_level: int = logging.INFO,
                 should_log_console: bool = True) -> None:
        """
        Initializes a custom logger that logs messages to both a file and optionally to the console.

        :param file_path: Path to the log file where logs will be saved.
        :param file_name: Name of the log file.
        :param log_level: default is logging.INFO.
        :param should_log_console: Flag indicating whether to log messages to the console.
        """
        super().__init__(file_name, level=log_level)
        self.propagate: bool = False
        self.file_path = file_path
        self.formatter: logging.Formatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] - [%(message)s]",
                                                              datefmt='%Y-%m-%d %H:%M:%S')

        file_handler: logging.FileHandler = logging.FileHandler(self.file_path, mode="w")
        file_handler.setFormatter(self.formatter)
        self.addHandler(file_handler)
        self.queue_handler: list = []
        if should_log_console:
            console_handler: logging.StreamHandler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            self.addHandler(console_handler)

    def log_message(self, level: int, message: str):
        """
        Logs a message with the specified log level.

        :param level: The log level.
        :param message: The message to log.
        """
        self.log(level, message)

    def close(self) -> None:
        """
        Closes all active log handlers.
        """
        handlers: list[logging.Handler] = self.handlers[:]
        for handler in handlers:
            self.removeHandler(handler)
            handler.close()
