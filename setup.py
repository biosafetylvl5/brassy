from setuptools import setup

setup(
    name="brassy",
    version="0.0.0",
    author="BSL5",
    entry_points={
        "console_scripts": ["brassy=src.brassy.brassy:run_from_CLI"],
    },
    install_requires=["argparse","rich"],
)
