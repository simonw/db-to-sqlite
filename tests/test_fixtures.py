import pytest

try:
    import MySQLdb
except ImportError:
    MySQLdb = None
try:
    import psycopg2
except ImportError:
    psycopg2 = None


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_fixture_mysql():
    db = MySQLdb.connect(user="root", passwd="", db="test_db_to_sqlite")
    cursor = db.cursor()
    cursor.execute("show tables")
    try:
        assert {("categories",), ("vendors",), ("products",)} == set(cursor.fetchall())
    finally:
        db.close()


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_fixture_postgresql():
    db = psycopg2.connect(user="postgres", dbname="test_db_to_sqlite")
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_catalog = 'test_db_to_sqlite'
        AND table_type = 'BASE TABLE'
        AND table_schema NOT IN ('information_schema', 'pg_catalog')
    """
    )
    rows = cursor.fetchall()
    assert {("categories",), ("vendors",), ("products",)} == set(rows)
