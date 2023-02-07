import pytest
import sqlite_utils
from sqlite_utils.db import ForeignKey
import sys

from .shared import all_databases


# This test was failing in CI on 3.9 and higher, I couldn't figure out why:
@pytest.mark.skipif(
    sys.version_info > (3, 8), reason="https://github.com/simonw/db-to-sqlite/issues/47"
)
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
        {"id": 1, "name": "***", "cat_id": 1, "vendor_id": "***", "price": None},
        {"id": 2, "name": "***", "cat_id": 1, "vendor_id": "***", "price": 2.1},
    ] == list(db["products"].rows)
    assert [
        ForeignKey(
            table="products",
            column="cat_id",
            other_table="categories",
            other_column="id",
        )
    ] == sorted(db["products"].foreign_keys)
