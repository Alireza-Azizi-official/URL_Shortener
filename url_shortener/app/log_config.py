import logging

logger = logging.getLogger("url_shortener")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s][%(name)s] %(message)s")
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)
