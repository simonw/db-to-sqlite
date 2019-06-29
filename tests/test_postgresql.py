import pytest
from .shared import shared_database_test


try:
    import psycopg2
except ImportError:
    psycopg2 = None


INIT_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id int not null primary key,
    name varchar(32) not null
);

CREATE TABLE IF NOT EXISTS vendors (
    id int not null primary key,
    name varchar(32) not null
);

CREATE TABLE IF NOT EXISTS products (
    id int not null primary key,
    name varchar(32) not null,
    cat_id int not null,
    vendor_id int,
    FOREIGN KEY (cat_id) REFERENCES categories(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

DELETE FROM products;
DELETE FROM categories;

INSERT INTO categories (id, name) VALUES (1, 'Junk');
INSERT INTO vendors (id, name) VALUES (1, 'Acme Corp');
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (1, 'Bobcat Statue', 1, 1);
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (2, 'Yoga Scarf', 1, null);
"""


@pytest.fixture(scope="session")
def postgresql_db():
    db = psycopg2.connect(user="postgres")
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute("SELECT datname FROM pg_database;")
    databases = [r[0] for r in cursor.fetchall()]
    if "test_db_to_sqlite" in databases:
        cursor.execute("DROP DATABASE test_db_to_sqlite;")
    cursor.execute("CREATE DATABASE test_db_to_sqlite;")
    cursor.close()
    db.commit()
    db.close()
    db = psycopg2.connect(user="postgres", dbname="test_db_to_sqlite")
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(INIT_SQL)
    db.commit()
    db.close()
    db = psycopg2.connect(user="postgres", dbname="test_db_to_sqlite")
    db.autocommit = True
    yield db
    db.close()


@pytest.mark.skipif(
    psycopg2 is None, reason="psycopg2 module not available - pip install psycopg2"
)
def test_fixture(postgresql_db):
    cursor = postgresql_db.cursor()
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
def test_db_to_sqlite_to_sqlite(postgresql_db, tmpdir):
    shared_database_test("postgresql://localhost/test_db_to_sqlite", tmpdir)
