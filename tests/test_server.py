"""Tests for the documentation server."""

import socket
import threading
import time
from pathlib import Path

import pytest
import requests

from sphinx_autodoc_vyper import cli, server


def test_server_start(tmp_path: Path) -> None:
    """Test server startup and accessibility."""
    # Create mock build directory
    build_dir = tmp_path / "docs" / "_build" / "html"
    build_dir.mkdir(parents=True)
    (build_dir / "index.html").write_text("<html><body>Test</body></html>")

    # Generate documentation
    cli._main(contracts_dir="", build_dir=str(build_dir), serve=False)

    # Start server in a thread
    port = _get_free_port()
    server_thread = threading.Thread(
        target=lambda: server.serve_docs(build_dir, port=port), daemon=True
    )
    server_thread.start()

    # Wait for server to start
    time.sleep(1)

    # Test server response
    try:
        response = requests.get(f"http://localhost:{port}")
        assert response.status_code == 200
        assert "Test" in response.text
    finally:
        # Cleanup (server will be stopped when thread is terminated)
        pass


def test_server_missing_docs(tmp_path: Path) -> None:
    """Test server behavior with missing documentation."""
    missing_path = tmp_path / "non-existant-dir"
    with pytest.raises(FileNotFoundError):
        server.serve_docs(missing_path)


def _get_free_port() -> int:
    """Get an available port number."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port  # type: ignore [no-any-return]
