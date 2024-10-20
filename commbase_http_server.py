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
# TODO: Description.

import http.server
import os
import sys
import ssl
from urllib.parse import unquote


class MultiDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directories=None, **kwargs):
        self.directories = directories
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        path = unquote(path)  # Handle URL encoding
        # Try matching the path to one of the passed directories
        for prefix, real_dir in self.directories.items():
            if path.startswith(prefix):
                return os.path.join(real_dir, path[len(prefix):].lstrip("/"))

        # Default to serving the current directory
        return super().translate_path(path)


def main():
    # Ensure at least one directory is passed
    if len(sys.argv) < 2:
        print("Usage: python script.py /dir1=/path/to/dir1 /dir2=/path/to/dir2 [--cert cert.pem --key key.pem]")
        sys.exit(1)

    # Parse directories from the command-line arguments
    directories = {}
    cert_file = None
    key_file = None

    for arg in sys.argv[1:]:
        if "=" in arg:
            prefix, path = arg.split("=", 1)
            directories[prefix] = os.path.abspath(path)
        elif arg == "--cert":
            cert_file = sys.argv[sys.argv.index(arg) + 1]
        elif arg == "--key":
            key_file = sys.argv[sys.argv.index(arg) + 1]
        else:
            if arg.startswith("--"):
                continue
            print(f"Invalid argument: {arg}")
            sys.exit(1)

    # Create the server with the custom handler
    server_address = ('127.0.0.1', 5050)
    handler = lambda *args, **kwargs: MultiDirectoryHTTPRequestHandler(*args, directories=directories, **kwargs)
    httpd = http.server.HTTPServer(server_address, handler)

    # Optionally wrap the server for HTTPS
    if cert_file and key_file:
        print(f"Enabling HTTPS with cert: {cert_file} and key: {key_file}")
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)

    print(f"Serving on {server_address}")
    print(f"Serving directories: {directories}")
    if cert_file and key_file:
        print(f"Server is running with HTTPS")
    else:
        print(f"Server is running with HTTP")

    httpd.serve_forever()


if __name__ == "__main__":
    main()
