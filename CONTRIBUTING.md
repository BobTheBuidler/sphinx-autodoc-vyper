# Contributing to Vyper Sphinx Docs

Thank you for your interest in contributing! This guide will help you get started with development.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/BobTheBuidler/sphinx-autodoc-vyper
cd sphinx-autodoc-vyper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Running Tests

The project uses tox for testing across multiple Python versions and environments:

```bash
# Run all tests and checks
tox

# Run specific environment
tox -e py39  # Run tests on Python 3.9
tox -e lint  # Run linting
tox -e type  # Run type checking

# Run pytest directly during development
pytest
pytest --cov=sphinx_autodoc_vyper
```

### Test Environments

- `py37` through `py311`: Run tests on Python 3.7-3.11
- `lint`: Run code formatting and linting checks
- `type`: Run type checking with mypy

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Black**: Code formatting
  ```bash
  black sphinx_autodoc_vyper tests
  ```

- **isort**: Import sorting
  ```bash
  isort sphinx_autodoc_vyper tests
  ```

- **Ruff**: Fast Python linter
  ```bash
  ruff check sphinx_autodoc_vyper tests
  ```

- **mypy**: Static type checking
  ```bash
  mypy sphinx_autodoc_vyper tests
  ```

## Project Structure

```
sphinx_autodoc_vyper/
├── __init__.py         # Package initialization
├── cli.py             # Command-line interface
├── generator.py       # Sphinx documentation generator
├── parser.py          # Vyper contract parser
└── server.py          # Development server

tests/
├── __init__.py
├── conftest.py        # Test fixtures
├── test_cli.py
├── test_generator.py
├── test_parser.py
└── test_server.py
```

## Making Changes

1. Create a new branch for your changes
2. Write tests for new functionality
3. Ensure all tests pass with `tox`
4. Update documentation if needed
5. Submit a pull request

## Documentation

When adding new features:
1. Add docstrings to new functions/classes
2. Update README.md if needed
3. Add example usage if applicable

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Publish to PyPI

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions