"""Console script for kune."""
import sys
import click
from .kune import create_socketio, create_app


@click.command()
@click.argument('html_file')
@click.option('--host', default='localhost')
@click.option('--port', default=5000)
def main(html_file, host, port):
    """kune serves an html file for live, synced presentations."""
    app = create_app(html_file)
    socketio = create_socketio(app)
    socketio.run(app, host=host, port=port)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
