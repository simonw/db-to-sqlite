import pytest
from . import shared


try:
    import psycopg2
except ImportError:
    psycopg2 = None


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_fixture():
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


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_db_to_sqlite_to_sqlite(tmpdir):
    shared.shared_database_test("postgresql://localhost/test_db_to_sqlite", tmpdir)


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_redact(tmpdir):
    shared.shared_redact_test("postgresql://localhost/test_db_to_sqlite", tmpdir)
