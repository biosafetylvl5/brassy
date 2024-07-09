from setuptools import setup

setup(
    name="brass",
    version="0.0.1a",
    author="BSL5",
    description="Build Release Assembler for Sane Software",
    entry_points={
        "console_scripts": ["brass=brass.brass:run_from_CLI"],
    },
    install_requires=["argparse", "rich", "pygit2", "rich-argparse"],
    python_requires=">3.5",
    packages=["brass"],
)
