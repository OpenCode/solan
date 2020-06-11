# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import click
from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import chdir
from socket import gethostname, gethostbyname
from pyngrok import ngrok


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
    solan_handler = SimpleHTTPRequestHandler
    solan_server_address = ('', port)
    httpd = solan_server(
        solan_server_address, solan_handler)
    # ----- Get local IP
    hostname = gethostname()
    ip = gethostbyname(hostname)
    click.echo(f'Local service active on {ip}:{port}')
    # ----- Enable remote access
    if remote:
        public_url = ngrok.connect(port)
        click.echo('Remote service active on {public_url}')
    # ----- Run server
    httpd.serve_forever()
