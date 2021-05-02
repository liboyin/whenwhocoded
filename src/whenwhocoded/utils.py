from contextlib import contextmanager
from logging import Logger, getLogger
from pathlib import Path
from typing import Generator


__all__ = ['sanitise_for_bokeh', 'split_lines', 'working_dir']

DEFAULT_LOGGER = getLogger(Path(__file__).stem)


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
