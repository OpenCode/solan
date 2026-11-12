# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import click
from http.server import HTTPServer
from os import chdir
from socket import socket, AF_INET, SOCK_DGRAM
from pyngrok import ngrok
from solan.handler import SolanHandler


def get_local_ip():
    # Use the interface of the default route; UDP connect sends no packets
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except OSError:
            return '127.0.0.1'


@click.command()
@click.option('-p', '--port', type=int,
              default=8000, show_default=True)
@click.option('-r', '--remote', is_flag=True)
@click.argument('directory',
                type=click.Path(exists=True))
def run(directory, port, remote):
    click.echo(f'Sharing {directory}')
    # ----- Change directory
    chdir(directory)
    click.echo('Running the server')
    # ----- Define server
    solan_server = HTTPServer
    solan_handler = SolanHandler
    solan_server_address = ('', port)
    httpd = solan_server(
        solan_server_address, solan_handler)
    # ----- Get local IP
    ip = get_local_ip()
    click.echo(f'Local service active on http://{ip}:{port}')
    # ----- Enable remote access
    if remote:
        public_url = ngrok.connect(port)
        click.echo(f'Remote service active on {public_url}')
    # ----- Run server
    httpd.serve_forever()
