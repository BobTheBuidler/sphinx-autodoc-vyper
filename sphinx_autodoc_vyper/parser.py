"""Parser for Vyper smart contracts."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

valid_ints = {f"int{8 * i}" for i in range(1, 32)}
valid_uints = {f"uint{8 * i}" for i in range(1, 32)}
VALID_VYPER_TYPES = {*valid_ints, *valid_uints, "address", "bool", "bytes32", "string"}

@dataclass
class Parameter:
    """Function parameter representation."""

    name: str
    type: str

    def __post_init__(self) -> None:
        if self.type not in VALID_VYPER_TYPES:
            raise ValueError(f"{self} is not a valid Vyper type")

@dataclass
class Function:
    """Vyper function representation."""

    name: str
    params: List[Parameter]
    return_type: Optional[str]
    docstring: Optional[str]

    def __post_init__(self) -> None:
        if self.return_type is not None and self.return_type not in VALID_VYPER_TYPES:
            raise ValueError(f"{self} does not return a valid Vyper type")

@dataclass
class Contract:
    """Vyper contract representation."""

    name: str
    path: str
    docstring: Optional[str]
    functions: List[Function]


class VyperParser:
    """Parser for Vyper smart contracts."""

    def __init__(self, contracts_dir: Path):
        if not contracts_dir.exists():
            raise FileNotFoundError(f"Invalid contracts dir: {contracts_dir}")
        self.contracts_dir = str(contracts_dir)

    def parse_contracts(self) -> List[Contract]:
        """Parse all Vyper contracts in the directory."""
        contracts = []
        for root, _, files in os.walk(self.contracts_dir):
            for file in files:
                if file.endswith(".vy"):
                    file_path = os.path.join(root, file)
                    contract = self._parse_contract(file_path)
                    contracts.append(contract)
        return contracts

    def _parse_contract(self, file_path: str) -> Contract:
        """Parse a single Vyper contract file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        name = os.path.basename(file_path).replace(".vy", "")
        rel_path = os.path.relpath(file_path, self.contracts_dir)

        # Extract contract docstring
        docstring = self._extract_contract_docstring(content)

        # Extract functions
        functions = self._extract_functions(content)

        return Contract(
            name=name, path=rel_path, docstring=docstring, functions=functions
        )

    def _extract_contract_docstring(self, content: str) -> Optional[str]:
        """Extract the contract's main docstring."""
        match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_functions(self, content: str) -> List[Function]:
        """Extract all functions from the contract, with @external functions listed first."""
        external_functions = []
        internal_functions = []
        function_pattern = (
            r'@(external|internal)\s+def\s+([^(]+)\(([^)]*)\)(\s*->\s*[^:]+)?:\s*("""[\s\S]*?""")?'
        )

        for match in re.finditer(function_pattern, content):
            decorator = match.group(1).strip()
            name = match.group(2).strip()
            params_str = match.group(3).strip()
            return_type = (
                match.group(4).replace("->", "").strip() if match.group(4) else None
            )
            docstring = match.group(5)[3:-3].strip() if match.group(5) else None

            params = self._parse_params(params_str)
            function = Function(
                name=name,
                params=params,
                return_type=return_type,
                docstring=docstring,
            )

            if decorator == "external":
                external_functions.append(function)
            else:
                internal_functions.append(function)

        # Combine external and internal functions, with external functions first
        return external_functions + internal_functions

    def _parse_params(self, params_str: str) -> List[Parameter]:
        """Parse function parameters."""
        if not params_str:
            return []

        params = []
        for param in params_str.split(","):
            if ":" in param:
                name, type_str = param.split(":")
                params.append(Parameter(name=name.strip(), type=type_str.strip()))
        return params
