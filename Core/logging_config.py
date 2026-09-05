import logging
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

request_id_var = ContextVar('request_id', default=None)
user_id_var = ContextVar('user_id', default=None)
formatter = jsonlogger.JsonFormatter(
    ['asctime', 'levelname', 'name', 'user_id', 'request_id', 'message']
)

class LoggerFilter(logging.Filter):

    def filter(self, record):
        record.user_id = user_id_var.get()
        record.request_id = request_id_var.get()
        return True

def setup_logging():

    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)


    file_handler = logging.FileHandler("app.json")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    file_handler.addFilter(LoggerFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    