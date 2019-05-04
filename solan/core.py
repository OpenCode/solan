# Copyright 2019 Francesco Apruzzese <cescoap@gmail.com>
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import click
import http.server
import os


@click.command()
@click.option('-p','--port', type=int, default=8000, show_default=True)
@click.argument('directory', type=click.Path(exists=True))
def run(directory, port):
    click.echo('Sharing {}'.format(directory))
    os.chdir(directory)
    click.echo('Running the server')
    solan_server = http.server.HTTPServer
    solan_handler = http.server.SimpleHTTPRequestHandler
    solan_server_address = ('', port)
    httpd = solan_server(solan_server_address, solan_handler)
    click.echo(
            "Service on {url}:{port}".format(
                url='XXXXXX',
                port=port))
    httpd.serve_forever()
