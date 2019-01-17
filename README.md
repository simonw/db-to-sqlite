# db-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/db-to-sqlite.svg)](https://pypi.python.org/pypi/db-to-sqlite)
[![Travis CI](https://travis-ci.org/simonw/db-to-sqlite.svg?branch=master)](https://travis-ci.org/simonw/db-to-sqlite)

CLI tool for exporting tables or queries from any SQL database to a SQLite file.

This is in extremely early stages of development - very much a 0.1.

    Usage: db-to-sqlite [OPTIONS] PATH

      Run a SQL query against any database and save the results to SQLite.

      https://github.com/simonw/db-to-sqlite
    
    Options:
      --version          Show the version and exit.
      --connection TEXT  SQLAlchemy connection string  [required]
      --sql TEXT         SQL query to run  [required]
      --table TEXT       Name of SQLite table to save the results  [required]
      --pk TEXT          Optional column to use as a primary key
      --help             Show this message and exit.

For example, to save the content of the `blog_entry` table from a PostgreSQL database to a local file called `blog.db` you could do this:

    db-to-sqlite blog.db \
        --connection="postgresql://localhost/myblog" \
        --sql="select * from blog_entry" \
        --table=blog_entry \
        --pk=id

