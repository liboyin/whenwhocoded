from bokeh.server.server import Server

from .bokeh_controller import main as app


# console_scripts must be a function
# https://packaging.python.org/specifications/entry-points/#use-for-scripts
def main() -> None:
    server = Server(app)
    server.start()
    server.io_loop.add_callback(server.show, '/')
    server.io_loop.start()
