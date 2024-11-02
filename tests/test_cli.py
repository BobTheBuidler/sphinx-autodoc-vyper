"""Tests for the command-line interface."""

from pathlib import Path

import pytest

from sphinx_autodoc_vyper.cli import main


def test_cli_basic(contracts_dir: Path, output_dir: Path, monkeypatch, capsys) -> None:  # type: ignore [o-untyped-def]
    """Test basic CLI functionality."""
    # Mock sys.argv
    monkeypatch.setattr(
        "sys.argv",
        ["vyper-docs", str(contracts_dir), "--output", str(output_dir)],
    )

    # Run CLI
    main()

    # Check output
    captured = capsys.readouterr()
    assert "Documentation built successfully" in captured.out

    # Check generated files
    docs_dir = output_dir / "docs"
    build_dir = docs_dir / "_build"
    assert docs_dir.exists()
    assert build_dir.exists()
    assert (build_dir / "html" / "index.html").exists()


def test_cli_invalid_contracts_dir(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore [o-untyped-def]
    """Test CLI with invalid contracts directory."""
    invalid_dir = tmp_path / "nonexistent"

    # Mock sys.argv
    monkeypatch.setattr("sys.argv", ["vyper-docs", str(invalid_dir)])

    # Run CLI and check for error
    with pytest.raises(FileNotFoundError):
        main()
