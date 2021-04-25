import argparse
from functools import partial
from pathlib import Path

from bokeh.server.server import Server

from .app import main

parser = argparse.ArgumentParser()
parser.add_argument('repo', type=Path)
parser.add_argument('-l', '--limit', type=int, default=9)
parser.add_argument('-i', '--include-files', nargs='*', default=[])
parser.add_argument('-e', '--exclude-files', nargs='*', default=[])
parser.add_argument('-c', '--use-cache', action='store_true', default=False)
args = parser.parse_args()
app = partial(main, args.repo, include_files=args.include_files, exclude_files=args.exclude_files,
              limit=args.limit, use_cache=args.use_cache)
server = Server(app)
server.start()
server.io_loop.add_callback(server.show, '/')
server.io_loop.start()