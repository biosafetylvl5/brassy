from setuptools import find_packages, setup

# This is JUST for local development

setup(
    name="brassy",
    version="0.0.0",
    author="BSL5",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["brassy=brassy.brassy:run_from_CLI"],
    },
    install_requires=[
        "argparse",
        "rich",
        "pygit2",
        "rich-argparse",
        "pyyaml",
        "platformdirs",
        "pydantic",
        "dateparser",
        "pinkrst",
        "black",
        "pytest",
        "sphinx-argparse",    # Required for Google-style docstrings
        "sphinxcontrib-runcmd",      # Required for running shell commands in documentation
        "sphinxcontrib-napoleon",    # Required for Google-style docstrings
        "sphinx-argparse",    # Required for Google-style docstrings
        "sphinx",                    # Required for building documentation, v7.2 errors
    ],
)
