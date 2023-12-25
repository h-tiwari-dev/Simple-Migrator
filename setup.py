import setuptools


setuptools.setup(
    name="simple_migrator",
    version="1.0",
    # scripts=["./scripts/install.sh"],
    author="Me",
    description="This runs my script which is great.",
    packages=setuptools.find_packages(),
    install_requires=[
        "setuptools",
        "build==1.0.3",
        "click==8.1.7",
        "packaging==23.2",
        "pip-tools==7.3.0",
        "pyproject-hooks==1.0.0",
        "sqlalchemy==2.0.23",
        "typing-extensions==4.9.0",
        "wheel==0.42.0",
    ],
    entry_points="""
      [console_scripts]
      simple_migrator=simple_migrator.migrator:cli
      """,
    python_requires=">=3.5",
)
