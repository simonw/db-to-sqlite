import itertools

import click
from sqlalchemy import create_engine, inspect, text
from sqlite_utils import Database
from fnmatch import fnmatch


@click.command()
@click.version_option()
@click.argument("connection")
@click.argument("path", type=click.Path(exists=False), required=True)
@click.option("--all", help="Detect and copy all tables", is_flag=True)
@click.option("--table", help="Specific tables to copy", multiple=True)
@click.option("--skip", help="When using --all skip these tables", multiple=True)
@click.option(
    "--redact",
    help="(table, column) pairs to redact with ***",
    nargs=2,
    type=str,
    multiple=True,
)
@click.option("--sql", help="Optional SQL query to run")
@click.option("--output", help="Table in which to save --sql query results")
@click.option("--pk", help="Optional column to use as a primary key")
@click.option(
    "--index-fks/--no-index-fks",
    default=True,
    help="Should foreign keys have indexes? Default on",
)
@click.option("-p", "--progress", help="Show progress bar", is_flag=True)
@click.option("--postgres-schema", help="PostgreSQL schema to use")
def cli(
    connection,
    path,
    all,
    table,
    skip,
    redact,
    sql,
    output,
    pk,
    index_fks,
    progress,
    postgres_schema,
):
    """
    Load data from any database into SQLite.

    PATH is a path to the SQLite file to create, e.c. /tmp/my_database.db

    CONNECTION is a SQLAlchemy connection string, for example:

        postgresql://localhost/my_database
        postgresql://username:passwd@localhost/my_database

        mysql://root@localhost/my_database
        mysql://username:passwd@localhost/my_database

    More: https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls
    """
    if not all and not table and not sql:
        raise click.ClickException("--all OR --table OR --sql required")
    if skip and not all:
        raise click.ClickException("--skip can only be used with --all")
    redact_columns = {}
    for table_name, column_name in redact:
        redact_columns.setdefault(table_name, set()).add(column_name)
    db = Database(path)
    if postgres_schema:
        conn_args = {"options": "-csearch_path={}".format(postgres_schema)}
    else:
        conn_args = {}
    if connection.startswith("postgres://"):
        connection = connection.replace("postgres://", "postgresql://")
    db_conn = create_engine(connection, connect_args=conn_args).connect()
    inspector = inspect(db_conn)
    # Figure out which tables we are copying, if any
    tables = table
    if all:
        tables = inspector.get_table_names()
    if tables:
        foreign_keys_to_add = []
        for i, table in enumerate(tables):
            if progress:
                click.echo("{}/{}: {}".format(i + 1, len(tables), table), err=True)
            if any(fnmatch(table, pattern) for pattern in skip):
                if progress:
                    click.echo("  ... skipping", err=True)
                continue
            pks = inspector.get_pk_constraint(table)["constrained_columns"]
            if len(pks) == 1:
                pks = pks[0]
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
            count = None
            table_quoted = db_conn.dialect.identifier_preparer.quote_identifier(table)
            if progress:
                count = db_conn.execute(
                    text("select count(*) from {}".format(table_quoted))
                ).fetchone()[0]
            results = db_conn.execute(text("select * from {}".format(table_quoted)))
            redact_these = redact_columns.get(table) or set()
            rows = (redacted_dict(r, redact_these) for r in results)
            # Make sure generator is not empty
            try:
                first = next(rows)
            except StopIteration:
                # This is an empty table - create an empty copy
                if not db[table].exists():
                    create_columns = {}
                    for column in inspector.get_columns(table):
                        try:
                            column_type = column["type"].python_type
                        except NotImplementedError:
                            column_type = str
                        create_columns[column["name"]] = column_type
                    db[table].create(create_columns)
            else:
                rows = itertools.chain([first], rows)
                if progress:
                    with click.progressbar(rows, length=count) as bar:
                        db[table].insert_all(bar, pk=pks, replace=True)
                else:
                    db[table].insert_all(rows, pk=pks, replace=True)
        foreign_keys_to_add_final = []
        for table, column, other_table, other_column in foreign_keys_to_add:
            # Make sure both tables exist and are not skipped - they may not
            # exist if they were empty and hence .insert_all() didn't have a
            # reason to create them.
            if (
                db[table].exists()
                and table not in skip
                and db[other_table].exists()
                and other_table not in skip
                # Also skip if this column is redacted
                and ((table, column) not in redact)
            ):
                foreign_keys_to_add_final.append(
                    (table, column, other_table, other_column)
                )
        if foreign_keys_to_add_final:
            # Add using .add_foreign_keys() to avoid running multiple VACUUMs
            if progress:
                click.echo(
                    "\nAdding {} foreign key{}\n{}".format(
                        len(foreign_keys_to_add_final),
                        "s" if len(foreign_keys_to_add_final) != 1 else "",
                        "\n".join(
                            "  {}.{} => {}.{}".format(*fk)
                            for fk in foreign_keys_to_add_final
                        ),
                    ),
                    err=True,
                )
            db.add_foreign_keys(foreign_keys_to_add_final)
    if sql:
        if not output:
            raise click.ClickException("--sql must be accompanied by --output")
        results = db_conn.execute(text(sql))
        rows = (dict(r._mapping) for r in results)
        db[output].insert_all(rows, pk=pk)
    if index_fks:
        db.index_foreign_keys()


def detect_primary_key(db_conn, table):
    inspector = inspect(db_conn)
    pks = inspector.get_pk_constraint(table)["constrained_columns"]
    if len(pks) > 1:
        raise click.ClickException("Multiple primary keys not currently supported")
    return pks[0] if pks else None


def redacted_dict(row, redact):
    d = dict(row._mapping)
    for key in redact:
        if key in d:
            d[key] = "***"
    return d


if __name__ == "__main__":
    cli()
