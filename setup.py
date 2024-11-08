from setuptools import find_packages, setup

setup(
    name="sphinx-autodoc-vyper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["sphinx>=4.0.0", "sphinx-rtd-theme>=1.0.0"],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "requests>=2.0.0",  # For testing server
        ]
    },
    entry_points={
        "console_scripts": ["sphinx-autodoc-vyper=sphinx_autodoc_vyper.cli:main"]
    },
    author="Vyper Developer",
    description="Sphinx documentation generator for Vyper smart contracts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BobTheBuidler/sphinx-autodoc-vyper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
