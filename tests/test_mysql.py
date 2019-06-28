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
CREATE TABLE IF NOT EXISTS categories(
   id int not null auto_increment primary key,
   name varchar(32) not null
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products(
   id int not null auto_increment primary key,
   name varchar(32) not null,
   cat_id int not null,
   FOREIGN KEY fk_cat(cat_id) REFERENCES categories(id)
   ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

DELETE FROM products;
DELETE FROM categories;

INSERT INTO categories (id, name) VALUES (1, "Junk");
INSERT INTO products (id, name, cat_id) VALUES (1, "Bobcat Statue", 1);
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
    assert (("categories",), ("products",)) == cursor.fetchall()


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_db_to_sqlite(mysql_db, tmpdir):
    connection = "mysql://root@localhost/test_db"
    db_path = str(tmpdir / "test.db")
    result = CliRunner().invoke(cli.cli, ["--connection", connection, "--all", db_path])
    db = sqlite_utils.Database(db_path)
    assert {"categories", "products"} == set(db.table_names())
    assert [{"id": 1, "name": "Bobcat Statue", "cat_id": 1}] == list(
        db["products"].rows
    )
    assert [{"id": 1, "name": "Junk"}] == list(db["categories"].rows)
    assert [
        ForeignKey(
            table="products",
            column="cat_id",
            other_table="categories",
            other_column="id",
        )
    ] == db["products"].foreign_keys
