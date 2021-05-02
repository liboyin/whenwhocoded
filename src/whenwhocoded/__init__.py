from logging.config import fileConfig
from pathlib import Path

fileConfig(Path(__file__).parents[2] / 'logging.conf', disable_existing_loggers=False)
