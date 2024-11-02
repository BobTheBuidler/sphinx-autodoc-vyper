"""Tests for the Sphinx documentation generator."""

from pathlib import Path

from sphinx_autodoc_vyper.generator import SphinxGenerator
from sphinx_autodoc_vyper.parser import (
    Contract,
    Function,
    Parameter,
    Struct,
    VyperParser,
)


def test_sphinx_generation(contracts_dir: Path, output_dir: Path) -> None:
    """Test complete Sphinx documentation generation."""
    # Parse contracts
    parser = VyperParser(contracts_dir)
    contracts = parser.parse_contracts()

    # Generate documentation
    generator = SphinxGenerator(str(output_dir))
    generator.generate(contracts)

    # Check generated files
    docs_dir = output_dir / "docs"
    assert docs_dir.exists()

    # Check conf.py
    conf_py = docs_dir / "conf.py"
    assert conf_py.exists()
    conf_content = conf_py.read_text()
    assert "sphinx.ext.autodoc" in conf_content
    assert "sphinx_rtd_theme" in conf_content

    # Check index.rst
    index_rst = docs_dir / "index.rst"
    assert index_rst.exists()
    index_content = index_rst.read_text()
    assert "Vyper Smart Contracts Documentation" in index_content
    assert "token" in index_content
    assert "nested_token" in index_content

    # Check contract documentation
    token_rst = docs_dir / "token.rst"
    assert token_rst.exists()
    token_content = token_rst.read_text()
    assert "ERC20 Token Implementation" in token_content
    assert "transfer" in token_content
    assert "balance_of" in token_content


def test_contract_rst_generation(contracts_dir: Path, output_dir: Path) -> None:
    """Test detailed RST file generation for contracts."""
    parser = VyperParser(contracts_dir)
    contracts = parser.parse_contracts()

    generator = SphinxGenerator(str(output_dir))
    generator.generate(contracts)

    # Check token.rst content
    token_rst = output_dir / "docs" / "token.rst"
    content = token_rst.read_text()

    # Check sections
    assert "token" in content
    assert "Functions" in content

    # Check function documentation
    assert ".. py:function:: transfer" in content
    assert "to: address" in content
    assert "amount: uint256" in content
    assert "-> bool" in content

    assert ".. py:function:: balance_of" in content
    assert "account: address" in content
    assert "-> uint256" in content

    # Check docstrings
    assert "Transfer tokens to a specified address" in content
    assert "Get the token balance of an account" in content


def test_generate_struct_docs() -> None:
    """Test struct documentation generation."""
    struct = Struct(
        name="MyStruct",
        fields=[
            Parameter(name="field1", type="uint256"),
            Parameter(name="field2", type="address"),
        ],
    )
    expected_output = (
        ".. py:class:: MyStruct\n\n"
        "   .. py:attribute:: MyStruct.field1\n\n"
        "      uint256\n"
        "   .. py:attribute:: MyStruct.field2\n\n"
        "      address"
    )
    assert SphinxGenerator._generate_struct_docs(struct) == expected_output


def test_generate_docs_for_contract_with_functions_and_structs() -> None:
    """Test documentation generation for a contract with both functions and structs."""
    contract = Contract(
        name="TestContract",
        docstring="This is a contract docstring.",
        structs=[
            Struct(
                name="MyStruct",
                fields=[
                    Parameter(name="field1", type="uint256"),
                    Parameter(name="field2", type="address"),
                ],
            )
        ],
        functions=[
            Function(
                name="transfer",
                params=[
                    Parameter(name="to", type="address"),
                    Parameter(name="amount", type="uint256"),
                ],
                return_type="bool",
                docstring="Transfer tokens to a specified address.",
            ),
            Function(
                name="balance_of",
                params=[Parameter(name="owner", type="address")],
                return_type="uint256",
                docstring="Get the balance of an account.",
            ),
        ],
    )

    generator = SphinxGenerator(".")
    docs = generator.generate([contract])

    # Expected documentation output
    expected_docs = (
        ".. py:class:: MyStruct\n\n"
        "   .. py:attribute:: MyStruct.field1\n\n"
        "      uint256\n"
        "   .. py:attribute:: MyStruct.field2\n\n"
        "      address\n\n"
        ".. py:function:: transfer(to: address, amount: uint256) -> bool\n\n"
        "   Transfer tokens to a specified address.\n\n"
        ".. py:function:: balance_of(owner: address) -> uint256\n\n"
        "   Get the balance of an account.\n\n"
    )

    assert docs == expected_docs
