import pytest
from .shared import shared_database_test


try:
    import MySQLdb
except ImportError:
    MySQLdb = None


INIT_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id int not null auto_increment primary key,
    name varchar(32) not null
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vendors (
    id int not null auto_increment primary key,
    name varchar(32) not null
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
"""


@pytest.fixture(scope="session")
def mysql_db():
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db_to_sqlite;")
    cursor.execute("USE test_db_to_sqlite;")
    cursor.execute(INIT_SQL)
    cursor.close()
    db.commit()
    db.close()
    db = MySQLdb.connect(user="root", passwd="", db="test_db_to_sqlite")
    yield db
    db.close()
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("DROP DATABASE test_db_to_sqlite;")
    cursor.close()
    db.commit()
    db.close()


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_fixture(mysql_db):
    cursor = mysql_db.cursor()
    cursor.execute("show tables")
    assert {("categories",), ("vendors",), ("products",)} == set(cursor.fetchall())


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_db_to_sqlite_to_sqlite(mysql_db, tmpdir):
    shared_database_test("mysql://root@localhost/test_db_to_sqlite", tmpdir)
