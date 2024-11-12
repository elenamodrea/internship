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
        super().__init__(file_name, level=log_level)
        self.propagate: bool = False
        formatter: logging.Formatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] - [%(message)s]",
                                                         datefmt='%Y-%m-%d %H:%M:%S')
        file_handler: logging.FileHandler = logging.FileHandler(file_path, mode="w")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

        if should_log_console:
            console_handler: logging.StreamHandler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)

    def log_message(self, level: int, message: str):
        self.log(level, message)

    def close(self) -> None:
        handlers: list[logging.Handler] = self.handlers[:]
        for handler in handlers:
            self.removeHandler(handler)
            handler.close()
