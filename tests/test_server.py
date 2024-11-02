"""Tests for the documentation server."""

import pytest
import socket
import threading
import time
import requests
from vyper_sphinx_docs.server import serve_docs


def test_server_start(tmp_path):
    """Test server startup and accessibility."""
    # Create mock build directory
    build_dir = tmp_path / "docs" / "_build" / "html"
    build_dir.mkdir(parents=True)
    (build_dir / "index.html").write_text("<html><body>Test</body></html>")
    
    # Start server in a thread
    port = _get_free_port()
    server_thread = threading.Thread(
        target=lambda: serve_docs(port=port),
        daemon=True
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


def test_server_missing_docs(tmp_path):
    """Test server behavior with missing documentation."""
    with pytest.raises(FileNotFoundError):
        serve_docs()


def _get_free_port():
    """Get an available port number."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port
