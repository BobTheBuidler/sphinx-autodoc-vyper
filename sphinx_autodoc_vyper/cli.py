"""Command-line interface for Vyper Sphinx documentation generator."""

import argparse
import os
import subprocess
from pathlib import Path
from .parser import VyperParser
from .generator import SphinxGenerator
from .server import serve_docs


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Generate Sphinx documentation for Vyper contracts')
    parser.add_argument('contracts_dir', help='Directory containing Vyper contracts')
    parser.add_argument('--output', '-o', default='.', help='Output directory for documentation')
    parser.add_argument('--serve', '-s', action='store_true', help='Serve documentation after building')
    parser.add_argument('--port', '-p', type=int, default=8000, help='Port for the documentation server')
    args = parser.parse_args()

    # Parse contracts
    vyper_parser = VyperParser(args.contracts_dir)
    contracts = vyper_parser.parse_contracts()

    # Generate Sphinx documentation
    generator = SphinxGenerator(args.output)
    generator.generate(contracts)

    # Build HTML documentation
    docs_dir = Path(args.output) / 'docs'
    build_dir = docs_dir / '_build'
    subprocess.run(['sphinx-build', '-b', 'html', str(docs_dir), str(build_dir)], check=True)
    
    print(f'Documentation built successfully in {build_dir}/html')
    
    # Serve documentation if requested
    if args.serve:
        serve_docs(args.port)