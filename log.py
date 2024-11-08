import logging

# Configure
logging.basicConfig(
    filename='log_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def message_logger(message, level):
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
