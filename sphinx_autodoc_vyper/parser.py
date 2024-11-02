"""Parser for Vyper smart contracts."""

import os
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Parameter:
    """Function parameter representation."""
    name: str
    type: str


@dataclass
class Function:
    """Vyper function representation."""
    name: str
    params: List[Parameter]
    return_type: Optional[str]
    docstring: Optional[str]


@dataclass
class Contract:
    """Vyper contract representation."""
    name: str
    path: str
    docstring: Optional[str]
    functions: List[Function]


class VyperParser:
    """Parser for Vyper smart contracts."""

    def __init__(self, contracts_dir: str):
        self.contracts_dir = contracts_dir

    def parse_contracts(self) -> List[Contract]:
        """Parse all Vyper contracts in the directory."""
        contracts = []
        for root, _, files in os.walk(self.contracts_dir):
            for file in files:
                if file.endswith('.vy'):
                    file_path = os.path.join(root, file)
                    contract = self._parse_contract(file_path)
                    contracts.append(contract)
        return contracts

    def _parse_contract(self, file_path: str) -> Contract:
        """Parse a single Vyper contract file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        name = os.path.basename(file_path).replace('.vy', '')
        rel_path = os.path.relpath(file_path, self.contracts_dir)
        
        # Extract contract docstring
        docstring = self._extract_contract_docstring(content)
        
        # Extract functions
        functions = self._extract_functions(content)
        
        return Contract(name=name, path=rel_path, docstring=docstring, functions=functions)

    def _extract_contract_docstring(self, content: str) -> Optional[str]:
        """Extract the contract's main docstring."""
        match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_functions(self, content: str) -> List[Function]:
        """Extract all functions from the contract."""
        functions = []
        function_pattern = r'@external\s+def\s+([^(]+)\(([^)]*)\)(\s*->\s*[^:]+)?:\s*("""[\s\S]*?""")?'
        
        for match in re.finditer(function_pattern, content):
            name = match.group(1).strip()
            params_str = match.group(2).strip()
            return_type = match.group(3).replace('->', '').strip() if match.group(3) else None
            docstring = match.group(4)[3:-3].strip() if match.group(4) else None
            
            params = self._parse_params(params_str)
            functions.append(Function(name=name, params=params, return_type=return_type, docstring=docstring))
            
        return functions

    def _parse_params(self, params_str: str) -> List[Parameter]:
        """Parse function parameters."""
        if not params_str:
            return []
            
        params = []
        for param in params_str.split(','):
            if ':' in param:
                name, type_str = param.split(':')
                params.append(Parameter(name=name.strip(), type=type_str.strip()))
        return params
