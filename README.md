# Vyper Sphinx Docs

A documentation generator for Vyper smart contracts using Sphinx. This tool automatically parses your Vyper contracts and generates beautiful, searchable documentation using Sphinx with the ReadTheDocs theme.

## Features

- Automatic parsing of Vyper smart contracts
- Extraction of docstrings and function signatures
- Beautiful Sphinx documentation with ReadTheDocs theme
- Support for nested contract directories
- Built-in documentation server
- Comprehensive test suite

## Installation

```bash
# Install from PyPI
pip install vyper-sphinx-docs

# Install with development dependencies
pip install "vyper-sphinx-docs[dev]"
```

## Quick Start

1. Generate documentation:
```bash
vyper-docs /path/to/contracts
```

2. Generate and serve documentation:
```bash
vyper-docs /path/to/contracts --serve
```

## Usage

```bash
# Basic usage
vyper-docs /path/to/contracts

# Specify custom output directory
vyper-docs /path/to/contracts -o /path/to/output

# Generate and serve documentation on port 8000
vyper-docs /path/to/contracts --serve

# Specify custom port
vyper-docs /path/to/contracts --serve --port 8080
```

## Example

For a Vyper contract like:

```python
"""
A simple ERC20 token implementation.
"""

@external
def transfer(to: address, amount: uint256) -> bool:
    """
    Transfer tokens to a specified address.
    
    Args:
        to: The recipient address
        amount: The amount of tokens to transfer
        
    Returns:
        bool: True if transfer succeeded
    """
    # Implementation
    return True
```

The generator will create Sphinx documentation with:
- Contract overview from the main docstring
- Function documentation with parameters and return types
- Proper RST formatting and navigation
- Search functionality
- Mobile-friendly responsive design

## Documentation Structure

The generated documentation follows this structure:
```
docs/
├── _build/          # Built HTML documentation
├── _static/         # Static assets
├── _templates/      # Sphinx templates
├── conf.py          # Sphinx configuration
├── index.rst        # Main index
└── contracts/       # Generated contract docs
```

## Requirements

- Python 3.7+
- Sphinx
- sphinx-rtd-theme

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see LICENSE file for details