"""Development server for viewing documentation."""

import http.server
import os
import socketserver
import webbrowser
from pathlib import Path
from typing import NoReturn


def serve_docs(build_dir: Path, port: int = 8000) -> NoReturn:  # type: ignore [misc]
    """Serve the documentation on a local development server."""

    if not build_dir.exists():
        raise FileNotFoundError(
            "Documentation not found. Run 'vyper-docs' first to generate the documentation."
        )

    os.chdir(build_dir)

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving documentation at {url}")
        webbrowser.open(url)
        httpd.serve_forever()
