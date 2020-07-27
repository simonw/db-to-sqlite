from setuptools import setup, find_packages
import io
import os

VERSION = "1.3"


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
        "test": ["pytest"],
        "test_mysql": ["pytest", "mysqlclient"],
        "test_postgresql": ["pytest", "psycopg2"],
        "mysql": ["mysqlclient"],
        "postgresql": ["psycopg2"],
    },
    tests_require=["db-to-sqlite[test]"],
    entry_points="""
        [console_scripts]
        db-to-sqlite=db_to_sqlite.cli:cli
    """,
    url="https://github.com/simonw/db-to-sqlite",
    project_urls={
        "Documentation": "https://github.com/simonw/db-to-sqlite/blob/master/README.md",
        "Changelog": "https://github.com/simonw/db-to-sqlite/releases",
        "Source code": "https://github.com/simonw/db-to-sqlite",
        "Issues": "https://github.com/simonw/db-to-sqlite/issues",
        "CI": "https://travis-ci.com/simonw/db-to-sqlite",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Database",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
