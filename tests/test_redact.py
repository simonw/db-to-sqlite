import sqlite_utils
from sqlite_utils.db import ForeignKey

from .shared import all_databases


@all_databases
def test_redact(connection, tmpdir, cli_runner):
    db_path = str(tmpdir / "test_redact.db")
    result = cli_runner(
        [
            connection,
            db_path,
            "--all",
            "--redact",
            "products",
            "name",
            "--redact",
            "products",
            "vendor_id",
        ]
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
