from setuptools import setup

setup(
    name="yarn",
    version="0.0.1a",
    author="BSL5",
    description="Yet Another Release Note generator",
    entry_points={
        "console_scripts": ["yarn=yarn.yarn:run_from_CLI"],
    },
    install_requires=["argparse", "rich", "pygit2", "rich-argparse"],
    python_requires=">3.5",
    packages=["yarn"],
)
