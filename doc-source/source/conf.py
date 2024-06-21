# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import sys, os

sys.path.insert(0, os.path.abspath("../../yarn"))

project = "Yarn"
author = "Gwyn Uttmark"
release = "0.0.1a"

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


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
