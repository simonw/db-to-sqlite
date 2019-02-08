import click
import sqlite3
from sqlalchemy import create_engine, inspect
from sqlite_utils import Database


@click.command()
@click.version_option()
@click.argument("path", type=click.Path(exists=False), required=True)
@click.option("--connection", required=True, help="SQLAlchemy connection string")
@click.option("--all", help="Detect and copy all tables", is_flag=True)
@click.option("--table", help="Name of table to save the results (and copy)")
@click.option("--sql", help="Optional SQL query to run")
@click.option("--pk", help="Optional column to use as a primary key")
def cli(path, connection, all, table, sql, pk):
    """
    Load data from any database into SQLite.
    
    https://github.com/simonw/db-to-sqlite
    """
    if not all and not table:
        raise click.ClickException("--all OR --table required")
    db = Database(path)
    db_conn = create_engine(connection).connect()
    if all:
        inspector = inspect(db_conn)
        for table in inspector.get_table_names():
            pk = detect_primary_key(db_conn, table)
            fks = inspector.get_foreign_keys(table)
            foreign_keys = [
                (
                    # column, type, other_table, other_column
                    fk["constrained_columns"][0],
                    "INTEGER",
                    fk["referred_table"],
                    fk["referred_columns"][0],
                )
                for fk in fks
            ]
            results = db_conn.execute("select * from {}".format(table))
            rows = (dict(r) for r in results)
            db[table].upsert_all(rows, pk=pk, foreign_keys=foreign_keys)
    else:
        if not sql:
            sql = "select * from {}".format(table)
            if not pk:
                pk = detect_primary_key(db_conn, table)
        results = db_conn.execute(sql)
        rows = (dict(r) for r in results)
        db[table].insert_all(rows, pk=pk)


def detect_primary_key(db_conn, table):
    inspector = inspect(db_conn)
    pks = inspector.get_pk_constraint(table)["constrained_columns"]
    if len(pks) > 1:
        raise click.ClickException("Multiple primary keys not currently supported")
    return pks[0] if pks else None
