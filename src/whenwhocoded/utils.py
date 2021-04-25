import logging
import sys
from contextlib import contextmanager
from logging import Logger
from pathlib import Path
from typing import Generator


__all__ = ['get_logger', 'sanitise_for_bokeh', 'split_lines', 'working_dir']


def get_logger(name: str) -> Logger:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s — %(levelname)s — %(name)s:%(lineno)d:%(funcName)s — %(message)s'))
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

DEFAULT_LOGGER = get_logger(Path(__file__).stem)


def sanitise_for_bokeh(text: str) -> str:
    from string import ascii_letters, digits
    allowed = ascii_letters + digits
    return ''.join(x if x in allowed else '_' for x in text)


def split_lines(text: str) -> Generator[str, None, None]:
    for x in text.splitlines():
        x = x.strip()
        if x:
            yield x


@contextmanager
def working_dir(p: Path, logger: Logger = DEFAULT_LOGGER):
    import os
    tmp = os.getcwd()
    logger.debug(f'Switching working dir from {tmp} to {p}')
    os.chdir(p)
    try:
        yield
    finally:
        os.chdir(tmp)
        logger.debug(f'Switching working dir from {p} to {tmp}')
