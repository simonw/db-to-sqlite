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
@click.option("--skip", help="When using --all skip these tables", multiple=True)
@click.option("--sql", help="Optional SQL query to run")
@click.option("--pk", help="Optional column to use as a primary key")
def cli(path, connection, all, table, skip, sql, pk):
    """
    Load data from any database into SQLite.
    
    https://github.com/simonw/db-to-sqlite
    """
    if not all and not table:
        raise click.ClickException("--all OR --table required")
    if skip and not all:
        raise click.ClickException("--skip can only be used with --all")
    db = Database(path)
    db_conn = create_engine(connection).connect()
    if all:
        inspector = inspect(db_conn)
        foreign_keys_to_add = []
        tables = inspector.get_table_names()
        for i, table in enumerate(tables):
            if table in skip:
                continue
            pks = inspector.get_pk_constraint(table)["constrained_columns"]
            if len(pks) > 1:
                click.echo("Multiple primary keys not currently supported", err=True)
                return
            pk = None
            if pks:
                pk = pks[0]
            fks = inspector.get_foreign_keys(table)
            foreign_keys_to_add.extend(
                [
                    (
                        # table, column, other_table, other_column
                        table,
                        fk["constrained_columns"][0],
                        fk["referred_table"],
                        fk["referred_columns"][0],
                    )
                    for fk in fks
                ]
            )
            results = db_conn.execute("select * from {}".format(table))
            rows = (dict(r) for r in results)
            db[table].upsert_all(rows, pk=pk)
        foreign_keys_to_add_final = []
        for table, column, other_table, other_column in foreign_keys_to_add:
            # Make sure both tables exist and are not skipped - they may not
            # exist if they were empty and hence .upsert_all() didn't have a
            # reason to create them
            if (
                db[table].exists
                and table not in skip
                and db[other_table].exists
                and other_table not in skip
            ):
                foreign_keys_to_add_final.append(
                    (table, column, other_table, other_column)
                )
        # Add using .add_foreign_keys() to avoid running multiple VACUUMs
        db.add_foreign_keys(foreign_keys_to_add_final)
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
