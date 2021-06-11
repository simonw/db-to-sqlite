import pytest
from sqlalchemy.engine.url import make_url
from .shared import MYSQL_TEST_DB_CONNECTION, POSTGRESQL_TEST_DB_CONNECTION

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
    bits = make_url(MYSQL_TEST_DB_CONNECTION)
    db = MySQLdb.connect(
        user=bits.username, passwd=bits.password or "", host=bits.host, db=bits.database
    )
    cursor = db.cursor()
    cursor.execute("show tables")
    try:
        assert {
            ("categories",),
            ("vendors",),
            ("products",),
            ("vendor_categories",),
            ("user",),
        } == set(cursor.fetchall())
    finally:
        db.close()


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_fixture_postgresql():
    bits = make_url(POSTGRESQL_TEST_DB_CONNECTION)
    db = psycopg2.connect(
        user=bits.username, password=bits.password, host=bits.host, dbname=bits.database
    )
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
    assert {
        ("categories",),
        ("vendor_categories",),
        ("products",),
        ("vendors",),
        ("user",),
    } == set(rows)
