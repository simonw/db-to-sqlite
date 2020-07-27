import pytest
from click.testing import CliRunner
from db_to_sqlite import cli

try:
    import MySQLdb
except ImportError:
    MySQLdb = None
try:
    import psycopg2
except ImportError:
    psycopg2 = None

MYSQL_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id int not null auto_increment primary key,
    name varchar(32) not null
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendors (
    id int not null auto_increment primary key,
    name varchar(32) not null
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendor_categories (
    cat_id int not null,
    vendor_id int not null,
    PRIMARY KEY (cat_id, vendor_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id int not null auto_increment primary key,
    name varchar(32) not null,
    cat_id int not null,
    vendor_id int,
    FOREIGN KEY fk_cat(cat_id) REFERENCES categories(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY fk_vendor(vendor_id) REFERENCES vendors(id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

DELETE FROM products;
DELETE FROM categories;

INSERT INTO categories (id, name) VALUES (1, "Junk");
INSERT INTO vendors (id, name) VALUES (1, "Acme Corp");
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (1, "Bobcat Statue", 1, 1);
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (2, "Yoga Scarf", 1, null);

INSERT INTO vendor_categories (cat_id, vendor_id)
    VALUES (1, 1);
"""

POSTGRESQL_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id int not null primary key,
    name varchar(32) not null
);

CREATE TABLE IF NOT EXISTS vendors (
    id int not null primary key,
    name varchar(32) not null
);

CREATE TABLE IF NOT EXISTS vendor_categories (
    cat_id int not null,
    vendor_id int not null,
    PRIMARY KEY (cat_id, vendor_id)
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
DELETE FROM vendors;
DELETE FROM vendor_categories;

INSERT INTO categories (id, name) VALUES (1, 'Junk');
INSERT INTO vendors (id, name) VALUES (1, 'Acme Corp');
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (1, 'Bobcat Statue', 1, 1);
INSERT INTO products (id, name, cat_id, vendor_id)
    VALUES (2, 'Yoga Scarf', 1, null);

INSERT INTO vendor_categories (cat_id, vendor_id)
    VALUES (1, 1);
"""


@pytest.fixture(autouse=True, scope="session")
def setup_mysql():
    if MySQLdb is None:
        yield
        return
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db_to_sqlite;")
    cursor.execute("USE test_db_to_sqlite;")
    cursor.execute(MYSQL_SQL)
    cursor.close()
    db.commit()
    db.close()
    yield
    # teardown_stuff
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("DROP DATABASE test_db_to_sqlite;")
    cursor.close()
    db.commit()
    db.close()


@pytest.fixture(autouse=True, scope="session")
def setup_postgresql():
    if psycopg2 is None:
        yield
        return
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
    cursor.execute(POSTGRESQL_SQL)
    db.commit()
    db.close()
    yield


@pytest.fixture
def cli_runner():
    def inner(args, **kwargs):
        return CliRunner().invoke(cli.cli, args, catch_exceptions=False, **kwargs)

    return inner
