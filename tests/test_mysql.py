import pytest
from . import shared

try:
    import MySQLdb
except ImportError:
    MySQLdb = None


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_fixture():
    db = MySQLdb.connect(user="root", passwd="", db="test_db_to_sqlite")
    cursor = db.cursor()
    cursor.execute("show tables")
    try:
        assert {("categories",), ("vendors",), ("products",)} == set(cursor.fetchall())
    finally:
        db.close()


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_db_to_sqlite(tmpdir):
    shared.shared_database_test("mysql://root@localhost/test_db_to_sqlite", tmpdir)


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_redact(tmpdir):
    shared.shared_redact_test("mysql://root@localhost/test_db_to_sqlite", tmpdir)
