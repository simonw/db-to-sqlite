# db-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/db-to-sqlite.svg)](https://pypi.python.org/pypi/db-to-sqlite)
[![Travis CI](https://travis-ci.com/simonw/db-to-sqlite.svg?branch=master)](https://travis-ci.com/simonw/db-to-sqlite)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/db-to-sqlite/blob/master/LICENSE)

CLI tool for exporting tables or queries from any SQL database to a SQLite file.

## Installation

Install from PyPI like so:

    pip install db-to-sqlite

If you want to use it with MySQL, you can install the extra dependency like this:

    pip install db-to-sqlite[mysql]

For PostgreSQL, use this:

    pip install db-to-sqlite[postgresql]

## Usage

    Usage: db-to-sqlite [OPTIONS] PATH

      Load data from any database into SQLite.

      https://github.com/simonw/db-to-sqlite

    Options:
      --version          Show the version and exit.
      --connection TEXT  SQLAlchemy connection string  [required]
      --all              Detect and copy all tables
      --table TEXT       Name of table to save the results (and copy)
      --skip TEXT        When using --all skip these tables
      --sql TEXT         Optional SQL query to run
      --pk TEXT          Optional column to use as a primary key
      -p, --progress     Show progress bar
      --help             Show this message and exit.

For example, to save the content of the `blog_entry` table from a PostgreSQL database to a local file called `blog.db` you could do this:

    db-to-sqlite blog.db \
        --connection="postgresql://localhost/myblog" \
        --table=blog_entry

You can also save the data from all of your tables, effectively creating a SQLite copy of your entire database. Any foreign key relationships will be detected and added to the SQLite database. For example:

    db-to-sqlite blog.db \
        --connection="postgresql://localhost/myblog" \
        --all

When running `--all` you can specify tables to skip using `--skip`:

    db-to-sqlite blog.db \
        --connection="postgresql://localhost/myblog" \
        --all \
        --skip=django_migrations

If you want to save the results of a custom SQL query, do this:

    db-to-sqlite output.db \
        --connection="postgresql://localhost/myblog" \
        --table=query_results \
        --sql="select id, title, created from blog_entry" \
        --pk=id
