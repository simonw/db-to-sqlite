import io
import os

from setuptools import find_packages, setup

VERSION = "1.5"


def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="db-to-sqlite",
    description="CLI tool for exporting tables or queries from any SQL database to a SQLite file",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    version=VERSION,
    license="Apache License, Version 2.0",
    packages=find_packages(),
    install_requires=["sqlalchemy", "sqlite-utils>=2.9.1", "click"],
    extras_require={
        "test": ["pytest", "pytest-timeout"],
        "test_mysql": ["pytest", "mysqlclient"],
        "test_postgresql": ["pytest", "psycopg2"],
        "mysql": ["mysqlclient"],
        "postgresql": ["psycopg2"],
    },
    python_requires=">=3.7",
    entry_points="""
        [console_scripts]
        db-to-sqlite=db_to_sqlite.cli:cli
    """,
    url="https://datasette.io/tools/db-to-sqlite",
    project_urls={
        "Documentation": "https://github.com/simonw/db-to-sqlite/blob/main/README.md",
        "Changelog": "https://github.com/simonw/db-to-sqlite/releases",
        "Source code": "https://github.com/simonw/db-to-sqlite",
        "Issues": "https://github.com/simonw/db-to-sqlite/issues",
        "CI": "https://travis-ci.com/simonw/db-to-sqlite",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Database",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
