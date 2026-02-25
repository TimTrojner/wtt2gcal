import logging
import os
from dotenv import load_dotenv

load_dotenv()


def setup_logging():
    """Configure structured logging with level from LOG_LEVEL env var."""
    level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    return logging.getLogger('urnik')
