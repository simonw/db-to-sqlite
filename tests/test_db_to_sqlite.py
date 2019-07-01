import sqlite_utils
from click.testing import CliRunner
from sqlite_utils.db import ForeignKey

from db_to_sqlite import cli

from .shared import all_databases


@all_databases
def test_db_to_sqlite(connection, tmpdir):
    db_path = str(tmpdir / "test.db")
    result = CliRunner().invoke(cli.cli, ["--connection", connection, "--all", db_path])
    db = sqlite_utils.Database(db_path)
    assert {"categories", "products", "vendors"} == set(db.table_names())
    assert [
        # Slight oddity: vendor_id comes out as a string even though MySQL
        # defined it as an integer because sqlite-utils treats mixed
        # integer + null as a string type, not an integer type
        {"id": 1, "name": "Bobcat Statue", "cat_id": 1, "vendor_id": "1"},
        {"id": 2, "name": "Yoga Scarf", "cat_id": 1, "vendor_id": None},
    ] == list(db["products"].rows)
    assert [{"id": 1, "name": "Junk"}] == list(db["categories"].rows)
    assert [
        ForeignKey(
            table="products",
            column="cat_id",
            other_table="categories",
            other_column="id",
        ),
        ForeignKey(
            table="products",
            column="vendor_id",
            other_table="vendors",
            other_column="id",
        ),
    ] == sorted(db["products"].foreign_keys)


@all_databases
def test_index_fks(connection, tmpdir):
    db_path = str(tmpdir / "test_with_fks.db")
    # With --no-index-fks should create no indexes
    CliRunner().invoke(
        cli.cli, ["--connection", connection, "--all", db_path, "--no-index-fks"]
    )
    db = sqlite_utils.Database(db_path)
    assert [] == db["products"].indexes
    # Without it (the default) it should create the indexes
    CliRunner().invoke(cli.cli, ["--connection", connection, "--all", db_path])
    db = sqlite_utils.Database(db_path)
    assert [["cat_id"], ["vendor_id"]] == [i.columns for i in db["products"].indexes]
