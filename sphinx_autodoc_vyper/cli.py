"""Command-line interface for Vyper Sphinx documentation generator."""

import argparse
import subprocess
from pathlib import Path

from .generator import SphinxGenerator
from .parser import VyperParser
from .server import serve_docs


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate Sphinx documentation for Vyper contracts"
    )
    parser.add_argument("contracts_dir", help="Directory containing Vyper contracts")
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory for documentation"
    )
    parser.add_argument(
        "--serve",
        "-s",
        action="store_true",
        help="Serve documentation after building",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port for the documentation server",
    )
    args = parser.parse_args()
    _main(args.contracts_dir, args.output)

    # Serve documentation if requested
    if args.serve:
        build_dir = Path(args.output) / "docs" / "_build"
        serve_docs(build_dir, port=args.port)


def _main(contracts_dir: str, output_dir: str) -> None:
    # Parse contracts
    vyper_parser = VyperParser(Path(contracts_dir))
    contracts = vyper_parser.parse_contracts()

    # Generate Sphinx documentation
    generator = SphinxGenerator(output_dir)
    generator.generate(contracts)

    # Build HTML documentation
    docs_dir = Path(output_dir) / "docs"
    build_dir = docs_dir / "_build" / "html"
    subprocess.run(
        ["sphinx-build", "-b", "html", str(docs_dir), str(build_dir), "-v"], check=True
    )

    print(f"Documentation built successfully in {build_dir}")
