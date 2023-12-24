# setup.py
from setuptools import setup, find_packages

setup(
    name="migrate",
    version="0.1",
    packages=find_packages(),
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "simple_migrator=simple_migrator.migrate:cli",
        ],
    },
)
