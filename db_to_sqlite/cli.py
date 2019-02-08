import click
import sqlite3
from sqlalchemy import create_engine, inspect
from sqlite_utils import Database


@click.command()
@click.version_option()
@click.argument("path", type=click.Path(exists=False), required=True)
@click.option("--connection", required=True, help="SQLAlchemy connection string")
@click.option("--sql", help="SQL query to run")
@click.option("--table", help="Name of SQLite table to save the results")
@click.option("--all", help="Detect and copy all tables", is_flag=True)
@click.option("--pk", help="Optional column to use as a primary key")
def cli(path, connection, sql, table, all, pk):
    """
    Run a SQL query against any database and save the results to SQLite.
    
    https://github.com/simonw/db-to-sqlite
    """
    if not all:
        if not table or not sql:
            click.echo("--all OR --table and --sql required", err=True)
            return
    db = Database(path)
    db_conn = create_engine(connection).connect()
    if all:
        inspector = inspect(db_conn)
        for table in inspector.get_table_names():
            pks = inspector.get_pk_constraint(table)["constrained_columns"]
            if len(pks) > 1:
                click.echo("Multiple primary keys not currently supported", err=True)
                return
            pk = None
            if pks:
                pk = pks[0]
            fks = inspector.get_foreign_keys(table)
            foreign_keys = [(
                # column, type, other_table, other_column
                fk["constrained_columns"][0],
                "INTEGER",
                fk["referred_table"],
                fk["referred_columns"][0],
            ) for fk in fks]
            results = db_conn.execute("select * from {}".format(table))
            rows = (dict(r) for r in results)
            db[table].upsert_all(rows, pk=pk, foreign_keys=foreign_keys)
    else:
        results = db_conn.execute(sql)
        rows = (dict(r) for r in results)
        db[table].insert_all(rows, pk=pk)
