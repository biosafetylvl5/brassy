from setuptools import setup, find_packages

setup(
    name="brassy",
    version="0.0.0",
    author="BSL5",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["brassy=brassy.brassy:run_from_CLI"],
    },
    install_requires=["argparse", "rich"],
)
