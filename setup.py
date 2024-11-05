from setuptools import setup, find_packages

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
        "pytest"
    ],
)
