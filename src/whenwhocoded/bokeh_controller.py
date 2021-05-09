from logging import getLogger
from pathlib import Path
from typing import List

from bokeh.document.document import Document
from bokeh.models import TextInput, Toggle

LOGGER = getLogger(Path(__file__).stem)


def logged_get_text_input(ti: TextInput) -> str:
    LOGGER.debug(f'TextInput.value: {ti.value}')
    return ti.value


def logged_get_toggle_input(t: Toggle) -> bool:
    LOGGER.debug(f'Toggle.active: {t.active}')
    return t.active


def get_path_input(ti: TextInput) -> Path:
    from .utils import ready_input_dir
    return ready_input_dir(logged_get_text_input(ti))


def get_tokens_input(ti: TextInput) -> List[str]:
    from .utils import split_and_strip
    return list(split_and_strip(logged_get_text_input(ti)))


def get_count_input(ti: TextInput) -> int:
    n = int(logged_get_text_input(ti))
    if 0 <= n <= 9:
        return n
    raise ValueError(n)


def main(doc: Document) -> None:
    from bokeh.layouts import layout
    from bokeh.models import Button
    from .bokeh_visualiser import main as plot
    repo_path = TextInput(title='Repository path:',value='../bokeh')
    include_files = TextInput(title='Include files:', value='.py .js')
    exclude_files = TextInput(title='Exclude files:', value='.csv')
    limit = TextInput(title='Top contributors (0-9):', value='9')
    use_cache = Toggle(label='Use cache (ignores include/exclude)', active=True)
    visualise = Button(label='Go', button_type='primary')
    visualise.on_click(lambda: plot(
        doc,
        get_path_input(repo_path),
        get_tokens_input(include_files),
        get_tokens_input(exclude_files),
        get_count_input(limit),
        logged_get_toggle_input(use_cache),
    ))
    doc.add_root(layout([[repo_path, include_files, exclude_files, limit], [use_cache, visualise]]))
