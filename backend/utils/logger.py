import logging
import sys

try:
    from backend.utils.security import scrub_pii
except ImportError:
    from utils.security import scrub_pii


class PiiFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = scrub_pii(record.msg)
        return True


def setup_logger():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('app.log')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.addFilter(PiiFilter())
    return logger


logger = setup_logger()
