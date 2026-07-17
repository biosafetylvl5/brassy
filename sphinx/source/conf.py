"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""


import sys
from pathlib import Path

sys.path.insert(0, Path("../../brassy").resolve())

project = "brassy"
author = "Gwyn Uttmark"
release = "0.0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxarg.ext",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # For Google and NumPy style docstrings
    "sphinx.ext.viewcode",
    "sphinxcontrib.runcmd",
]
templates_path = ["_templates"]
exclude_patterns = []

# Render docstring "Attributes" sections as :ivar: field-list entries instead
# of separate autodoc directives -- autodoc's :members: already documents each
# attribute from the class body, and generating both causes Sphinx to warn
# about duplicate object descriptions.
napoleon_use_ivar = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
