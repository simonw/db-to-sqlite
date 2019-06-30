from click.testing import CliRunner
from db_to_sqlite import cli
import sqlite_utils
from sqlite_utils.db import ForeignKey


def shared_database_test(connection, tmpdir):
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


def shared_redact_test(connection, tmpdir):
    db_path = str(tmpdir / "test_reduct.db")
    result = CliRunner().invoke(
        cli.cli,
        [
            "--connection",
            connection,
            "--all",
            db_path,
            "--redact",
            "products",
            "name",
            "--redact",
            "products",
            "vendor_id",
        ],
    )
    assert 0 == result.exit_code, (result.output, result.exception)
    db = sqlite_utils.Database(db_path)
    assert [
        {"id": 1, "name": "***", "cat_id": 1, "vendor_id": "***"},
        {"id": 2, "name": "***", "cat_id": 1, "vendor_id": "***"},
    ] == list(db["products"].rows)
    assert [
        ForeignKey(
            table="products",
            column="cat_id",
            other_table="categories",
            other_column="id",
        )
    ] == sorted(db["products"].foreign_keys)
