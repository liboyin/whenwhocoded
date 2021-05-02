from pathlib import Path
from typing import Iterable

import pandas as pd
from bokeh.plotting import Document, Figure

from .repo_history import main as get_stats


def transform(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    import numpy as np
    assert limit < 10, limit
    df = np.cumsum(df.fillna(0).astype(int), axis=0)
    # sort authors by total contribution
    df.sort_values(by=df.index[-1], axis=1, ascending=False, inplace=True)
    if df.shape[1] > limit:
        others = df.iloc[:, limit:].sum(axis=1)
        df.drop(labels=df.columns[limit:], axis=1, inplace=True)
        df['others'] = others
    df['zeros'] = 0
    return df.reset_index()


def render(df: pd.DataFrame) -> Figure:
    from bokeh.models import HoverTool
    from bokeh.palettes import Category10_10
    from bokeh.plotting import ColumnDataSource
    p = Figure(plot_width=1200, plot_height=600, x_axis_type='datetime')
    names = [x for x in df.columns.tolist() if x not in ('date', 'zeros')]
    source = ColumnDataSource(df)
    p.varea_stack(stackers=names, x='date', color=Category10_10[:len(names)], legend_label=names, source=source)
    p.line(x='date', y='zeros', line_alpha=0, source=source)
    p.legend.location = 'top_left'
    p.add_tools(HoverTool(
        tooltips=[('date', '@date{%Y-%m-%d}')] + [(x, f'@{x}') for x in names],
        formatters={'@date': 'datetime'},
        mode='vline'
    ))
    return p


def main(repo: Path,
         doc: Document,
         include_files: Iterable[str] = (),
         exclude_files: Iterable[str] = (),
         limit: int = 9,
         use_cache: bool = False) -> None:
    from bokeh.models import Panel, Tabs
    df = get_stats(repo, include_files, exclude_files, use_cache)
    commits_df = df[['author', 'date', 'files']].pivot_table(values='files', index='date', columns='author', aggfunc='count')
    files_df = df[['author', 'date', 'files']].pivot_table(values='files', index='date', columns='author', aggfunc='sum')
    lines_df = df[['author', 'date', 'lines']].pivot_table(values='lines', index='date', columns='author', aggfunc='sum')
    doc.add_root(Tabs(tabs=[
        Panel(title='Commits', child=render(transform(commits_df, limit))),
        Panel(title='Files', child=render(transform(files_df, limit))),
        Panel(title='Lines', child=render(transform(lines_df, limit))),
    ]))
