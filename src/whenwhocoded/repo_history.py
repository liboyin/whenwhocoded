import re
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd

from .utils import get_logger, sanitise_for_bokeh, split_lines, working_dir

DIFF_PATTERN = re.compile(r'(\d+) files? changed(, (\d+) insertions?\(\+\))?(, (\d+) deletions?\(\-\))?')
LOGGER = get_logger(Path(__file__).stem)


def logged_fetch_cache(p: Path) -> pd.DataFrame:
    LOGGER.info('Using cache file. include_files and exclude_files are ignored.')
    result = pd.read_csv(p, parse_dates=['date'])
    LOGGER.debug(f'Finished reading from {p}')
    return result


def make_diff_suffix(include_files: Iterable[str], exclude_files: Iterable[str]) -> str:
    suffixes = []
    for x in include_files:
        suffixes.append(f"'*{x}'" if x.startswith('.') else f"'*.{x}'")
    for x in exclude_files:
        suffixes.append(f"':!*{x}'" if x.startswith('.') else f"':!*.{x}'")
    result = ' '.join(suffixes)
    LOGGER.info(f'Created git diff suffix: {result}')
    return result


def get_all_commits(author_email: bool = False) -> List[str]:
    if author_email:
        # email is more stable if domain names are the same
        cmd = r"git --no-pager log --reflog --no-merges --pretty=format:'%H %P (%ae) %as'"
    else:
        cmd = r"git --no-pager log --reflog --no-merges --pretty=format:'%H %P (%an) %as'"
    LOGGER.debug(f'About to run subprocess: {cmd}')
    result = subprocess.check_output(cmd, shell=True)
    LOGGER.debug(f'Finished running subprocess: {cmd}')
    return list(split_lines(result.decode()))


def get_diff_line(parent: str, child: str, suffix: str) -> str:
    cmd = f"git --no-pager diff --ignore-cr-at-eol --shortstat {parent}..{child}"
    if suffix:
        cmd = f'{cmd} -- {suffix}'
    return subprocess.check_output(cmd, shell=True).decode().strip()


def parse_commit_line(text: str) -> Tuple[str, str, str, str]:
    hashes, tail = text.split(' (', maxsplit=1)
    hashes = hashes.strip()
    if ' ' not in hashes:
        # empty repo hash
        hashes += ' 4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    child, parent = hashes.split()
    author, date = tail.rsplit(') ', maxsplit=1)
    return parent, child, author.strip(), date.strip()


def parse_diff_line(text: str) -> Tuple[int, int, int]:
    if not text:
        return (0, 0, 0)
    m = re.match(DIFF_PATTERN, text)
    files = int(m[1])  # type: ignore
    insertions = int(m[3] or 0)  # type: ignore
    deletions = int(m[5] or 0)  # type: ignore
    return files, insertions, deletions


def parse_commit(line: str, diff_suffix: str) -> Tuple[str, str, str, str, int, int]:
    parent, child, author, date = parse_commit_line(line)
    author = sanitise_for_bokeh(author.split('@', maxsplit=1)[0])
    files, insertions, deletions = parse_diff_line(get_diff_line(parent, child, diff_suffix))
    return child, parent, author, date, files, insertions + deletions


def logged_write_cache(p: Path, df: pd.DataFrame) -> None:
    LOGGER.debug(f'About to write to {p}')
    df.to_csv(p, index=False)
    LOGGER.debug(f'Finished writing to {p}')


def get_commit_history(include_files: Iterable[str],
                       exclude_files: Iterable[str],
                       use_cache: bool) -> pd.DataFrame:
    from tqdm import tqdm
    cache_path = Path('commit_history.csv')
    if use_cache and cache_path.is_file():
        return logged_fetch_cache(cache_path)
    diff_suffix = make_diff_suffix(include_files, exclude_files)
    # display a progress bar here
    data = [parse_commit(line, diff_suffix) for line in tqdm(get_all_commits(), ascii=True, ncols=75)]
    df = pd.DataFrame(data, columns=['commit', 'parent', 'author', 'date', 'files', 'lines'])
    logged_write_cache(cache_path, df)
    df['date'] = pd.to_datetime(df['date'])
    return df


def main(repo_path: Path,
         include_files: Iterable[str] = (),
         exclude_files: Iterable[str] = (),
         use_cache: bool = False) -> pd.DataFrame:
    with working_dir(repo_path, LOGGER):
        df = get_commit_history(include_files, exclude_files, use_cache)
        return df.groupby(['author', 'date']).aggregate(sum).reset_index()
