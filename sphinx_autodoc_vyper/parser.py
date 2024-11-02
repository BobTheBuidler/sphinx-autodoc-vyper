"""Parser for Vyper smart contracts."""

import logging
import os
import re
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Union

logger = logging.getLogger(__name__)

valid_ints = {f"int{8 * (i+1)}" for i in range(32)}
valid_uints = {f"uint{8 * (i+1)}" for i in range(32)}
VALID_VYPER_TYPES = {*valid_ints, *valid_uints, "address", "bool", "Bytes", "String"}

ENUM_PATTERN = r"enum\s+(\w+)\s*:\s*([\w\s\n]+)"
CONSTANT_PATTERN = r"(\w+):\s*constant\((\w+)\)\s*=\s*(.*?)$"
VARIABLE_PATTERN = r"(\w+):\s*(public\((\w+)\)|(\w+))"
STRUCT_PATTERN = r"struct\s+(\w+)\s*{([^}]*)}"
EVENT_PATTERN = r"event\s+(\w+)\((.*?)\)"
FUNCTION_PATTERN = r'@(external|internal)\s+def\s+([^(]+)\(([^)]*)\)(\s*->\s*[^:]+)?:\s*("""[\s\S]*?""")?'
PARAM_PATTERN = r"(\w+:\s*DynArray\[[^\]]+\]|\w+:\s*\w+)"


@dataclass
class Enum:
    """Vyper enum representation."""

    name: str
    values: List[str]

    def generate_docs(self) -> str:
        content = f".. py:class:: {self.name}\n\n"
        for value in self.values:
            content += f"   .. py:attribute:: {value}\n\n"
        return content


@dataclass
class Constant:
    """Vyper constant representation."""

    name: str
    type: str
    value: Any

    def __post_init__(self) -> None:
        if self.type is not None and self.type not in VALID_VYPER_TYPES:
            logger.warning(f"{self} is not a valid Vyper type")

    def generate_docs(self) -> str:
        return f".. py:data:: {self.name}\n\n   {self.type}: {self.value}\n\n"


@dataclass
class Variable:
    """Vyper variable representation."""

    name: str
    type: str
    visibility: str

    def __post_init__(self) -> None:
        if self.type not in VALID_VYPER_TYPES:
            logger.warning(f"{self} is not a valid Vyper type")


@dataclass
class Tuple:
    """Vyper tuple representation."""

    types: List[str]

    def __post_init__(self) -> None:
        # strip whitespace
        self.types = [type_str.strip() for type_str in self.types]

        # validate types
        for type in self.types:
            if type not in VALID_VYPER_TYPES:
                logger.warning(f"{self} is not a valid Vyper type")

    def __len__(self) -> int:
        return len(self.types)


@dataclass
class DynArray:
    """Dynamic length array representation."""

    type: str
    max_length: Union[int, Constant]

    def __post_init__(self) -> None:
        if self.type not in VALID_VYPER_TYPES:
            logger.warning(f"{self} is not a valid Vyper type")


Type = Union[str, Tuple, DynArray]


@dataclass
class Parameter:
    """Function parameter representation."""

    name: str
    type: Type

    def __post_init__(self) -> None:
        if self.type.startswith("DynArray"):  # type: ignore [union-attr]
            assert self.type.endswith("]")  # type: ignore [union-attr]
            type, max_length = self.type[:-1].split("[")[1].split(",")  # type: ignore [index]
            try:
                self.type = DynArray(type, int(max_length))
            except ValueError:
                # TODO: include type and value info
                constant = Constant(name=max_length.strip(), type=None, value=None)  # type: ignore [arg-type]
                self.type = DynArray(type, constant)
        elif self.type not in VALID_VYPER_TYPES:
            logger.warning(f"{self} is not a valid Vyper type")


@dataclass
class Struct:
    """Vyper struct representation."""

    name: str
    fields: List[Parameter]


@dataclass
class EventParameter:
    """Vyper event parameter representation."""

    name: str
    type: str
    indexed: bool

    def __post_init__(self) -> None:
        if self.type not in VALID_VYPER_TYPES:
            logger.warning(f"{self} is not a valid Vyper type")


@dataclass
class Event:
    """Vyper event representation."""

    name: str
    params: List[EventParameter]

    def generate_docs(self) -> str:
        content = f".. py:class:: {event.name}\n\n"
        for field in event.fields:
            type_str = f"indexed({field.type})" if field.indexed else field.type
            content += f"   .. py:attribute:: {field.name}\n\n"
            content += f"      {type_str}\n\n"
        return content


@dataclass
class Function:
    """Vyper function representation."""

    name: str
    params: List[Parameter]
    return_type: Optional[Type]
    docstring: Optional[str]

    def __post_init__(self) -> None:
        if self.return_type is not None:
            if self.return_type.startswith("("):  # type: ignore [union-attr]
                self.return_type = Tuple(self.return_type[1:-1].split(","))  # type: ignore [index]
            elif self.return_type not in VALID_VYPER_TYPES:
                logger.warning(f"{self} does not return a valid Vyper type")


@dataclass
class Contract:
    """Vyper contract representation."""

    name: str
    path: str
    docstring: Optional[str]
    enums: List[Enum]
    structs: List[Struct]
    events: List[Event]
    constants: List[Constant]
    variables: List[Variable]
    external_functions: List[Function]
    internal_functions: List[Function]


Functions = typing.Tuple[List[Function], List[Function]]


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

        external_functions, internal_functions = self._extract_functions(content)

        return Contract(
            name=name,
            path=rel_path,
            docstring=self._extract_contract_docstring(content),
            enums=self._extract_enums(content),
            structs=self._extract_structs(content),
            events=self._extract_events(content),
            constants=self._extract_constants(content),
            variables=self._extract_variables(content),
            external_functions=external_functions,
            internal_functions=internal_functions,
        )

    def _extract_contract_docstring(self, content: str) -> Optional[str]:
        """Extract the contract's main docstring."""
        match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_enums(content: str) -> List[Enum]:
        """Extract all enums from the contract."""
        return [
            Enum(
                name=match.group(1).strip(),
                values=[
                    value.strip()
                    for value in match.group(2).split("\n")
                    if value.strip()
                ],
            )
            for match in re.finditer(ENUM_PATTERN, content)
        ]

    def _extract_constants(self, content: str) -> List[Constant]:
        """Extract constants from the contract."""
        return [
            Constant(
                name=match.group(1).strip(),
                type=match.group(2).strip(),
                value=match.group(3).strip(),
            )
            for match in re.finditer(CONSTANT_PATTERN, content, re.MULTILINE)
        ]

    @staticmethod
    def _extract_variables(content: str) -> List[Variable]:
        """Extract all contract-level variables from the contract."""
        # Split the content into lines and filter out lines that are likely inside functions
        lines = content.splitlines()
        contract_level_lines = []
        inside_function = False

        for line in lines:
            stripped_line = line.strip()
            # Detect function definitions to avoid parsing their contents
            if stripped_line.startswith("@") or stripped_line.startswith("def "):
                inside_function = True
            elif stripped_line == "":
                inside_function = False

            # Only consider lines outside of functions
            if not inside_function and stripped_line:
                contract_level_lines.append(stripped_line)

        # Join the filtered lines back into a single string for regex processing
        filtered_content = "\n".join(contract_level_lines)

        return [
            Variable(
                name=match.group(1).strip(),
                type=match.group(3).strip()
                if match.group(3)
                else match.group(4).strip(),
                visibility="public" if match.group(2) else "private",
            )
            for match in re.finditer(VARIABLE_PATTERN, filtered_content)
        ]

    @classmethod
    def _extract_structs(cls, content: str) -> List[Struct]:
        """Extract all structs from the contract."""
        return [
            Struct(
                name=match.group(1).strip(),
                fields=cls._parse_params(match.group(2).strip()),
            )
            for match in re.finditer(STRUCT_PATTERN, content)
        ]

    @staticmethod
    def _extract_events(content: str) -> List[Event]:
        """Extract all events from the contract."""
        return [
            Event(
                name=match.group(1).strip(),
                params=self._parse_event_params(match.group(2).strip()),
            )
            for match in re.finditer(EVENT_PATTERN, content)
        ]

    @classmethod
    def _extract_functions(cls, content: str) -> Functions:
        """Extract all functions from the contract, with @external functions listed first."""
        external_functions = []
        internal_functions = []

        for match in re.finditer(FUNCTION_PATTERN, content):
            decorator = match.group(1).strip()
            name = match.group(2).strip()
            params_str = match.group(3).strip()
            return_type = (
                match.group(4).replace("->", "").strip() if match.group(4) else None
            )
            docstring = match.group(5)[3:-3].strip() if match.group(5) else None

            function = Function(
                name=name,
                params=cls._parse_params(params_str),
                return_type=return_type,
                docstring=docstring,
            )

            if decorator == "external":
                external_functions.append(function)
            else:
                internal_functions.append(function)

        return external_functions, internal_functions

    @staticmethod
    def _parse_params(params_str: str) -> List[Parameter]:
        """Parse function parameters."""
        if not params_str:
            return []

        params = []
        # Use regex to split by commas that are not within brackets
        for param in re.finditer(PARAM_PATTERN, params_str):
            name, type_str = param.group().split(":")
            type_str = type_str.strip()
            typ = Tuple(type_str[1:-1].split(",")) if type_str[1] == "(" else type_str
            params.append(Parameter(name=name.strip(), type=typ))
        return params

    @staticmethod
    def _parse_event_params(params_str: str) -> List[EventParameter]:
        """Parse event parameters."""
        params = []
        for param_str in params_str.split("\n"):
            name, type = param_str.strip().split(":")
            type = type.strip()
            if indexed := "indexed" in type:
                assert type.startswith("indexed(") and type.endswith(")"), type
                type = type[8:-1]
            param = EventParameter(name=name.strip(), type=type, indexed=indexed)
            params.append(param)
        return params
