import pytest
from click.testing import CliRunner
from db_to_sqlite import cli
import sqlite_utils
from sqlite_utils.db import ForeignKey

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
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db;")
    cursor.execute("USE test_db;")
    cursor.execute(INIT_SQL)
    cursor.close()
    db.commit()
    db.close()
    db = MySQLdb.connect(user="root", passwd="", db="test_db")
    yield db
    db.close()
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("DROP DATABASE test_db;")
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
def test_db_to_sqlite(mysql_db, tmpdir):
    connection = "mysql://root@localhost/test_db"
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
