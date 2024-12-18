"""Sphinx documentation generator for Vyper contracts."""

import os
from typing import List

from .parser import Contract, Function, Struct

INDEX_RST = """Vyper Smart Contracts Documentation
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

"""


CONF_CONTENT = """# Configuration file for Sphinx documentation

project = 'Vyper Smart Contracts'
copyright = '2023'
author = 'Vyper Developer'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
"""


class SphinxGenerator:
    """Generate Sphinx documentation for Vyper contracts."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.docs_dir = os.path.join(output_dir, "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

    def generate(self, contracts: List[Contract]) -> None:
        """Generate Sphinx documentation."""
        self._generate_conf_py()
        self._generate_index_rst(contracts)
        self._generate_contract_docs(contracts)

    def _generate_conf_py(self) -> None:
        """Generate Sphinx configuration file."""
        with open(os.path.join(self.docs_dir, "conf.py"), "w", encoding="utf-8") as f:
            f.write(CONF_CONTENT)

    def _generate_index_rst(self, contracts: List[Contract]) -> None:
        """Generate index.rst file."""
        content = INDEX_RST
        for contract in contracts:
            content += f"   {contract.name}\n"

        with open(os.path.join(self.docs_dir, "index.rst"), "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_contract_docs(self, contracts: List[Contract]) -> None:
        """Generate documentation for each contract."""
        for contract in contracts:
            content = f"{contract.name}\n{'=' * len(contract.name)}\n\n"

            if contract.docstring:
                content += f"{contract.docstring}\n\n"

            if contract.structs:
                content += "Structs\n---------\n\n"
                for struct in contract.structs:
                    content += self._generate_struct_docs(struct)

            if contract.functions:
                content += "Functions\n---------\n\n"
                for func in contract.functions:
                    content += self._generate_function_docs(func)

            with open(
                os.path.join(self.docs_dir, f"{contract.name}.rst"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write(content)

    @staticmethod
    def _generate_function_docs(func: Function) -> str:
        params = ", ".join(f"{p.name}: {p.type}" for p in func.params)
        return_type = f" -> {func.return_type}" if func.return_type else ""

        content = f".. py:function:: {func.name}({params}){return_type}\n\n"
        if func.docstring:
            content += f"   {func.docstring}\n\n"
        return content

    @staticmethod
    def _generate_struct_docs(struct: Struct) -> str:
        content = f".. py:class:: {func.name}\n\n"
        for field in struct.fields:
            content += f"   .. py:attribute:: {struct.name}.{field.name}\n\n"
            content += f"      {field.type}"
        return content
