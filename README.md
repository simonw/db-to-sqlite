# db-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/db-to-sqlite.svg)](https://pypi.python.org/pypi/db-to-sqlite)
[![Changelog](https://img.shields.io/github/v/release/simonw/db-to-sqlite?include_prereleases&label=changelog)](https://github.com/simonw/db-to-sqlite/releases)
[![Travis CI](https://travis-ci.com/simonw/db-to-sqlite.svg?branch=master)](https://travis-ci.com/simonw/db-to-sqlite)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/db-to-sqlite/blob/master/LICENSE)

CLI tool for exporting tables or queries from any SQL database to a SQLite file.

## Installation

Install from PyPI like so:

    pip install db-to-sqlite

If you want to use it with MySQL, you can install the extra dependency like this:

    pip install db-to-sqlite[mysql]

Installing the `mysqlclient` library on OS X can be tricky - I've found [this recipe](https://gist.github.com/simonw/90ac0afd204cd0d6d9c3135c3888d116) to work (run that before installing `db-to-sqlite`).

For PostgreSQL, use this:

    pip install db-to-sqlite[postgresql]

## Usage

    Usage: db-to-sqlite [OPTIONS] CONNECTION PATH

      Load data from any database into SQLite.

      PATH is a path to the SQLite file to create, e.c. /tmp/my_database.db

      CONNECTION is a SQLAlchemy connection string, for example:

          postgresql://localhost/my_database
          postgresql://username:passwd@localhost/my_database

          mysql://root@localhost/my_database
          mysql://username:passwd@localhost/my_database

      More: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls

    Options:
      --version                     Show the version and exit.
      --all                         Detect and copy all tables
      --table TEXT                  Specific tables to copy
      --skip TEXT                   When using --all skip these tables
      --redact TEXT...              (table, column) pairs to redact with ***
      --sql TEXT                    Optional SQL query to run
      --output TEXT                 Table in which to save --sql query results
      --pk TEXT                     Optional column to use as a primary key
      --index-fks / --no-index-fks  Should foreign keys have indexes? Default on
      -p, --progress                Show progress bar
      --help                        Show this message and exit.

For example, to save the content of the `blog_entry` table from a PostgreSQL database to a local file called `blog.db` you could do this:

    db-to-sqlite "postgresql://localhost/myblog" blog.db \
        --table=blog_entry

You can specify `--table` more than once.

You can also save the data from all of your tables, effectively creating a SQLite copy of your entire database. Any foreign key relationships will be detected and added to the SQLite database. For example:

    db-to-sqlite "postgresql://localhost/myblog" blog.db \
        --all

When running `--all` you can specify tables to skip using `--skip`:

    db-to-sqlite "postgresql://localhost/myblog" blog.db \
        --all \
        --skip=django_migrations

If you want to save the results of a custom SQL query, do this:

    db-to-sqlite "postgresql://localhost/myblog" output.db \
        --output=query_results \
        --sql="select id, title, created from blog_entry" \
        --pk=id

The `--output` option specifies the table that should contain the results of the query.

## Using db-to-sqlite with Heroku Postgres

If you run an application on [Heroku](https://www.heroku.com/) using their [Postgres database product](https://www.heroku.com/postgres), you can use the `heroku config` command to access a compatible connection string:

    $ heroku config --app myappname | grep HEROKU_POSTG
    HEROKU_POSTGRESQL_OLIVE_URL: postgres://username:password@ec2-xxx-xxx-xxx-x.compute-1.amazonaws.com:5432/dbname

You can pass this to `db-to-sqlite` to create a local SQLite database with the data from your Heroku instance.

You can even do this using a bash one-liner:

    $ db-to-sqlite $(heroku config --app myappname | grep HEROKU_POSTG | cut -d: -f 2-) \
        /tmp/heroku.db --all -p
    1/23: django_migrations
    ...
    17/23: blog_blogmark
    [####################################]  100%
    ...

## Related projects

* [Datasette](https://github.com/simonw/datasette): A tool for exploring and publishing data. Works great with SQLite files generated using `db-to-sqlite`.
* [sqlite-utils](https://github.com/simonw/sqlite-utils): Python CLI utility and library for manipulating SQLite databases.
* [csvs-to-sqlite](https://github.com/simonw/csvs-to-sqlite): Convert CSV files into a SQLite database.
