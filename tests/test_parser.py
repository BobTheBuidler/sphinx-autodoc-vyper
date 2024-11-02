"""Tests for the Vyper contract parser."""

import pytest
from pathlib import Path
from sphinx_autodoc_vyper.parser import VyperParser, Contract, Function, Parameter


def test_parse_contracts(contracts_dir: Path) -> None:
    """Test parsing multiple contracts."""
    parser = VyperParser(str(contracts_dir))
    contracts = parser.parse_contracts()

    assert len(contracts) == 2
    assert any(c.name == "token" for c in contracts)
    assert any(c.name == "nested_token" for c in contracts)


def test_contract_parsing(contracts_dir: Path) -> None:
    """Test detailed contract parsing."""
    parser = VyperParser(str(contracts_dir))
    contracts = parser.parse_contracts()
    contract = next(c for c in contracts if c.name == "token")

    # Test contract properties
    assert isinstance(contract, Contract)
    assert contract.docstring is not None
    assert "ERC20 Token Implementation" in contract.docstring

    # Test functions
    assert len(contract.functions) == 2
    transfer_func = next(f for f in contract.functions if f.name == "transfer")
    balance_func = next(f for f in contract.functions if f.name == "balance_of")

    # Test transfer function
    assert isinstance(transfer_func, Function)
    assert len(transfer_func.params) == 2
    assert transfer_func.return_type == "bool"
    assert transfer_func.docstring is not None
    assert "Transfer tokens" in transfer_func.docstring

    # Test balance_of function
    assert isinstance(balance_func, Function)
    assert len(balance_func.params) == 1
    assert balance_func.return_type == "uint256"
    assert balance_func.docstring is not None
    assert "Get the token balance" in balance_func.docstring


def test_parameter_parsing(contracts_dir: Path) -> None:
    """Test function parameter parsing."""
    parser = VyperParser(str(contracts_dir))
    contracts = parser.parse_contracts()
    contract = next(c for c in contracts if c.name == "token")
    transfer_func = next(f for f in contract.functions if f.name == "transfer")

    # Test parameters
    assert len(transfer_func.params) == 2
    to_param = transfer_func.params[0]
    amount_param = transfer_func.params[1]

    assert isinstance(to_param, Parameter)
    assert to_param.name == "to"
    assert to_param.type == "address"

    assert isinstance(amount_param, Parameter)
    assert amount_param.name == "amount"
    assert amount_param.type == "uint256"


def test_empty_contract(tmp_path: Path) -> None:
    """Test parsing an empty contract."""
    contracts_dir = tmp_path / "contracts"
    contracts_dir.mkdir()

    empty_contract = contracts_dir / "empty.vy"
    empty_contract.write_text("")

    parser = VyperParser(str(contracts_dir))
    contracts = parser.parse_contracts()

    assert len(contracts) == 1
    assert contracts[0].name == "empty"
    assert contracts[0].docstring is None
    assert len(contracts[0].functions) == 0
