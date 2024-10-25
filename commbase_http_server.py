#!/usr/bin/env python
################################################################################
#                             commbase-http-server                             #
#                                                                              #
# AI Powered Conversational Assistant for Computers and Droids                 #
#                                                                              #
# Change History                                                               #
# 10/19/2024  Esteban Herrera Original code.                                   #
#                           Add new history entries as needed.                 #
#                                                                              #
#                                                                              #
################################################################################
################################################################################
################################################################################
#                                                                              #
#  Copyright (c) 2022-present Esteban Herrera C.                               #
#  stv.herrera@gmail.com                                                       #
#                                                                              #
#  This program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 3 of the License, or           #
#  (at your option) any later version.                                         #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program; if not, write to the Free Software                 #
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #

# commbase_http_server.sh
# This Python script implements a custom HTTP/HTTPS server that can serve files
# from a single directory. It extends the built-in
# http.server.SimpleHTTPRequestHandler to allow mapping specific URL paths to
# designated local directories.

# Example usage:
# Using the default host and port:
# python commbase_http_server.py $COMMBASE_APP_DIR/src/web_app/
# Using a custom host and port:
# python commbase_http_server.py $COMMBASE_APP_DIR/src/web_app/ --host 127.0.0.1 --port 5050
# With SSL certificate:
# python commbase_http_server.py $COMMBASE_APP_DIR/src/web_app/ --host 127.0.0.1 --port 5050 --cert cert.pem --key key.pem

# To create a generic (self-signed) SSL certificate:
# openssl genpkey -algorithm RSA -out key.pem
# openssl req -new -x509 -key key.pem -out cert.pem -days 365

# Important notes:
# For localhost development, this code will work just fine and allow you to
# test SSL if needed. However, for distribuited environments or handling higher
# loads and concurrent requests, it’s recommended to use more advanced tools
# like nginx or gunicorn.

import http.server
import os
import sys
import ssl
from urllib.parse import unquote


class SingleDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom HTTP request handler that serves files from a single directory.

    This handler extends the SimpleHTTPRequestHandler to serve files from
    a specified directory based on the request path.

    Attributes:
        root_dir (str): The absolute path of the directory to serve.

    Methods:
        translate_path(path):
            Translates a given URL path into a local filesystem path, serving
            files from the specified directory.
    """

    def __init__(self, *args, root_dir=None, **kwargs):
        self.root_dir = root_dir
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        path = unquote(path)  # Handle URL encoding

        # Serve the requested file from the specified root directory
        return os.path.join(self.root_dir, path.lstrip("/"))


def main():
    """
    Main function to start the HTTP/HTTPS server for serving files from
    a single directory with custom base URL and port.

    This function parses command-line arguments to configure the server,
    including the directory, base URL, and port to serve, as well as optional
    SSL certificate/key files for enabling HTTPS.

    Usage:
        python commbase_http_server.py /path/to/dir --host 127.0.0.1 --port
        5050 [--cert cert.pem --key key.pem]

    Raises:
        SystemExit: If no directory is specified or if command-line
        arguments are invalid.
    """
    # Parse directory, base URL, port, and optional cert/key arguments
    root_dir = None
    base_url = '127.0.0.1'  # Default host
    port = 5050  # Default port
    cert_file = None
    key_file = None

    args = sys.argv[1:]

    if len(args) > 0:
        root_dir = os.path.abspath(args[0])  # First argument is the directory
    else:
        print("Usage: python commbase_http_server.py /path/to/dir --host 127.0.0.1 --port 5050 [--cert /path/to/cert.pem --key /path/to/key.pem]")
        sys.exit(1)

    for i in range(1, len(args)):
        if args[i] == "--host" and i + 1 < len(args):
            base_url = args[i + 1]
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif args[i] == "--cert" and i + 1 < len(args):
            cert_file = args[i + 1]
        elif args[i] == "--key" and i + 1 < len(args):
            key_file = args[i + 1]

    # Create the server with the custom handler
    server_address = (base_url, port)
    handler = lambda *args, **kwargs: SingleDirectoryHTTPRequestHandler(*args, root_dir=root_dir, **kwargs)
    httpd = http.server.HTTPServer(server_address, handler)

    # Optionally wrap the server for HTTPS
    if cert_file and key_file:
        print(f"Enabling HTTPS with cert: {cert_file} and key: {key_file}")
        # Create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving on {base_url}:{port}")
    print(f"Serving directory: {root_dir}")
    if cert_file and key_file:
        print("Server is running with HTTPS")
    else:
        print("Server is running with HTTP")

    httpd.serve_forever()


if __name__ == "__main__":
    main()
