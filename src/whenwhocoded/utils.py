from contextlib import contextmanager
from logging import Logger, getLogger
from pathlib import Path
from typing import Generator, Optional, Union


__all__ = ['ready_input_dir', 'sanitise_for_bokeh', 'split_and_strip', 'splitlines_and_strip', 'working_dir']

DEFAULT_LOGGER = getLogger(Path(__file__).stem)


def ready_input_dir(path: Union[str, Path]) -> Path:
    path = Path(path)
    if not path.is_dir():
        if path.exists():
            raise NotADirectoryError(path)
        raise FileNotFoundError(path)
    return path


def sanitise_for_bokeh(text: str) -> str:
    from string import ascii_letters, digits
    allowed = ascii_letters + digits
    return ''.join(x if x in allowed else '_' for x in text)


def split_and_strip(text: str,
                    sep: Optional[str] = None,
                    maxsplit: int = -1) -> Generator[str, None, None]:
    for x in text.split(sep, maxsplit):
        if x := x.strip():
            yield x


def splitlines_and_strip(text: str) -> Generator[str, None, None]:
    for x in text.splitlines():
        if x := x.strip():
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
