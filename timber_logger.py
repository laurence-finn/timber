import logging

class TimberLogger:

    def __init__(self):
        self.logger = logging.getLogger("Timber")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("timber.log", encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message):
        self.logger.info(message)

    def close_log(self):
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers = []