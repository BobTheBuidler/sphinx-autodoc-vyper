"""Development server for viewing documentation."""

import http.server
import os
import webbrowser
from pathlib import Path
from typing import NoReturn


def serve_docs(build_dir: Path, port: int = 8000) -> NoReturn:  # type: ignore [misc]
    """Serve the documentation on a local development server."""

    html_dir = build_dir / "html"

    if not html_dir.exists():
        raise FileNotFoundError(
            "Documentation not found. Run 'sphinx-autodoc-vyper' first to generate the documentation."
        )

    os.chdir(html_dir)

    with http.server.HTTPServer(
        ("", port),
        http.server.SimpleHTTPRequestHandler,
    ) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving documentation at {url}")
        webbrowser.open(url)
        httpd.serve_forever()
