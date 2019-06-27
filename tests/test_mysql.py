import pytest

try:
    import MySQLdb
except ImportError:
    MySQLdb = None


INIT_SQL = """
CREATE TABLE IF NOT EXISTS foo (id integer primary key);
"""


@pytest.fixture(scope="session")
def db():
    db = MySQLdb.connect(user="root", passwd="")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")
    cursor.execute(INIT_SQL)
    yield db
    cursor = db.cursor()
    cursor.execute("DROP DATABASE test_db")
    db.close()


@pytest.mark.skipif(
    MySQLdb is None, reason="MySQLdb module not available - pip install mysqlclient"
)
def test_mysql(db):
    cursor = db.cursor()
    cursor.execute("show tables")
    assert (("foo",),) == cursor.fetchall()
