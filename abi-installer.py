#!/usr/bin/env python3
"""FruitBang browser installer — Python stdlib HTTP server + HTML wizard."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from http.server import HTTPServer
from lib.server import Handler
from lib.state import LOG_PATH, MARKER_PATH

__version__ = "0.1.0"

PORT = 7777


def main():
    """Truncate the log, then start the HTTP server bound to localhost only."""
    if os.path.exists(MARKER_PATH):
        print(f"[abi] WARNING: a previous install did not finish cleanly "
              f"({MARKER_PATH} still present). Check /mnt and disk state "
              "manually before starting a new install.", file=sys.stderr)
    open(LOG_PATH, "w").close()
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"FruitBang installer running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
