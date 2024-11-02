"""Tests for the Vyper contract parser."""

from pathlib import Path

from sphinx_autodoc_vyper.parser import (
    Contract,
    Function,
    Parameter,
    Tuple,
    VyperParser,
)


def test_parse_contracts(contracts_dir: Path) -> None:
    """Test parsing multiple contracts."""
    parser = VyperParser(contracts_dir)
    contracts = parser.parse_contracts()

    assert len(contracts) == 2
    assert any(c.name == "token" for c in contracts)
    assert any(c.name == "nested_token" for c in contracts)


def test_contract_parsing(contracts_dir: Path) -> None:
    """Test detailed contract parsing."""
    parser = VyperParser(contracts_dir)
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
    parser = VyperParser(contracts_dir)
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

    parser = VyperParser(contracts_dir)
    contracts = parser.parse_contracts()

    assert len(contracts) == 1
    assert contracts[0].name == "empty"
    assert contracts[0].docstring is None
    assert len(contracts[0].functions) == 0


def test_extract_contract_docstring() -> None:
    """Test contract docstring extraction."""
    content = '''"""
    This is a contract docstring.
    """
    @external
    def foo() -> bool:
        pass
    '''
    parser = VyperParser(Path("."))
    docstring = parser._extract_contract_docstring(content)
    assert docstring == "This is a contract docstring."


def test_extract_structs() -> None:
    """Test struct extraction from contract."""
    content = """
    struct MyStruct {
        field1: uint256
        field2: address
    }
    """
    parser = VyperParser(Path("."))
    structs = parser._extract_structs(content)
    assert len(structs) == 1
    assert structs[0].name == "MyStruct"
    assert len(structs[0].fields) == 2
    assert structs[0].fields[0].name == "field1"
    assert structs[0].fields[0].type == "uint256"
    assert structs[0].fields[1].name == "field2"
    assert structs[0].fields[1].type == "address"


def test_parse_contract_with_functions_and_structs() -> None:
    """Test parsing a contract with both functions and structs."""
    contract_content = '''
    """
    This is a contract docstring.
    """

    struct MyStruct:
        field1: uint256
        field2: address

    @external
    def transfer(to: address, amount: uint256) -> bool:
        """
        Transfer tokens to a specified address.
        """
        return True

    @external
    def balance_of(owner: address) -> uint256:
        """
        Get the balance of an account.
        """
        return 0
    '''

    parser = VyperParser(Path("."))
    # Use the actual content to parse
    parser.parse_contracts = lambda x: [parser._parse_contract(contract_content)]
    parser._extract_contract_docstring = lambda x: parser._extract_contract_docstring(contract_content)  # type: ignore [method-assign,assignment]
    parser._extract_structs = lambda x: parser._extract_structs(contract_content)  # type: ignore [method-assign,assignment]
    parser._extract_functions = lambda x: parser._extract_functions(contract_content)  # type: ignore [method-assign,assignment]

    contract = parser.parse_contracts()[0]

    # Assertions for structs
    assert len(contract.structs) == 1
    assert contract.structs[0].name == "MyStruct"
    assert len(contract.structs[0].fields) == 2
    assert contract.structs[0].fields[0].name == "field1"
    assert contract.structs[0].fields[0].type == "uint256"
    assert contract.structs[0].fields[1].name == "field2"
    assert contract.structs[0].fields[1].type == "address"

    # Assertions for functions
    assert len(contract.functions) == 2
    assert contract.functions[0].name == "transfer"
    assert len(contract.functions[0].params) == 2
    assert contract.functions[0].params[0].name == "to"
    assert contract.functions[0].params[0].type == "address"
    assert contract.functions[0].params[1].name == "amount"
    assert contract.functions[0].params[1].type == "uint256"
    assert contract.functions[0].return_type == "bool"

    assert contract.functions[1].name == "balance_of"
    assert len(contract.functions[1].params) == 1
    assert contract.functions[1].params[0].name == "owner"
    assert contract.functions[1].params[0].type == "address"
    assert contract.functions[1].return_type == "uint256"


def test_tuple_length() -> None:
    """Test the length of a Tuple instance."""
    tuple_instance = Tuple(types=["uint256", "address", "bool"])
    assert len(tuple_instance) == 3

    empty_tuple_instance = Tuple(types=[])
    assert len(empty_tuple_instance) == 0
