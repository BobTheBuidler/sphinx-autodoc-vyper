"""Pytest configuration and fixtures."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def sample_contract():
    """Sample Vyper contract content."""
    return '''"""
ERC20 Token Implementation
This is a sample ERC20 token contract.
"""

@external
def transfer(to: address, amount: uint256) -> bool:
    """
    Transfer tokens to a specified address.
    
    Args:
        to: The recipient address
        amount: The amount to transfer
        
    Returns:
        bool: Success status
    """
    return True

@external
def balance_of(account: address) -> uint256:
    """
    Get the token balance of an account.
    
    Args:
        account: The address to query
        
    Returns:
        uint256: Token balance
    """
    return 0
'''


@pytest.fixture
def contracts_dir(tmp_path, sample_contract):
    """Create a temporary directory with sample contracts."""
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    
    # Create main contract
    contract_file = contracts / "token.vy"
    contract_file.write_text(sample_contract)
    
    # Create nested contract
    nested_dir = contracts / "nested"
    nested_dir.mkdir()
    nested_contract = nested_dir / "nested_token.vy"
    nested_contract.write_text(sample_contract)
    
    return contracts


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output
