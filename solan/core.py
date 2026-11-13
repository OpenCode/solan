# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import sys
from contextlib import contextmanager
from errno import EADDRINUSE
from http.server import HTTPServer
from socket import AF_INET, SOCK_DGRAM, socket

import click
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError

from solan.handler import SolanHandler


def get_local_ip():
    # Use the interface of the default route; UDP connect sends no packets
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


class SolanServer(HTTPServer):
    # On Windows SO_REUSEADDR lets a second server bind a port that is already in use,
    # so "address already in use" would never be reported: enable it only elsewhere
    allow_reuse_address = os.name != "nt"


@contextmanager
def silenced_stderr():
    # The ngrok process writes its own errors straight to stderr: send them to the void
    # while it starts (it inherits the redirection), solan reports them in a cleaner way
    try:
        sys.stderr.flush()
        saved = os.dup(2)
    except (AttributeError, OSError, ValueError):
        # No usable stderr (e.g. detached process): nothing to silence
        yield
        return
    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), 2)
            yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)


@click.command()
@click.option("-p", "--port", type=int, default=8000, show_default=True)
@click.option("-r", "--remote", is_flag=True)
@click.argument("directory", type=click.Path(exists=True))
def run(directory, port, remote):
    click.echo(f"Sharing {directory}")
    # ----- Change directory
    os.chdir(directory)
    click.echo("Running the server")
    # ----- Define server
    solan_server = SolanServer
    solan_handler = SolanHandler
    solan_server_address = ("", port)
    try:
        httpd = solan_server(solan_server_address, solan_handler)
    except OSError as error:
        if error.errno != EADDRINUSE:
            raise
        raise click.ClickException(f"Address already in use: port {port}") from None
    # ----- Get local IP
    ip = get_local_ip()
    click.echo(f"Local service active on http://{ip}:{port}")
    # ----- Enable remote access
    if remote:
        # Errors are reported below; don't let pyngrok dump ngrok's raw log
        logging.getLogger("pyngrok").addHandler(logging.NullHandler())
        try:
            with silenced_stderr():
                public_url = ngrok.connect(port)
        except PyngrokNgrokError as error:
            # ngrok reports escaped newlines: keep only the first, meaningful line
            details = (error.ngrok_error or str(error)).replace("\\r", "").replace("\\n", "\n").strip()
            if "ERR_NGROK_4018" in details:
                raise click.ClickException(
                    "Remote access requires an ngrok account. "
                    "Get your authtoken at https://dashboard.ngrok.com/get-started/your-authtoken "
                    "and set it in the NGROK_AUTHTOKEN environment variable."
                ) from None
            raise click.ClickException(f"ngrok could not start: {details.splitlines()[0]}") from None
        click.echo(f"Remote service active on {public_url}")
    # ----- Run server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        click.echo("\nStopped")
    finally:
        httpd.server_close()
