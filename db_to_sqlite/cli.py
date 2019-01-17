import click
import sqlite3
from sqlalchemy import create_engine
from sqlite_utils import Database


@click.command()
@click.version_option()
@click.argument("path", type=click.Path(exists=False), required=True)
@click.option("--connection", required=True, help="SQLAlchemy connection string")
@click.option("--sql", required=True, help="SQL query to run")
@click.option("--table", required=True, help="Name of SQLite table to save the results")
@click.option("--pk", help="Optional column to use as a primary key")
def cli(path, connection, sql, table, pk):
    """
    Run a SQL query against any database and save the results to SQLite.
    
    https://github.com/simonw/db-to-sqlite
    """
    db = Database(path)
    db_conn = create_engine(connection).connect()
    results = db_conn.execute(sql)
    rows = [dict(r) for r in results]
    db[table].insert_all(rows, pk=pk)
