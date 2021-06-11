import pytest
import os

try:
    import MySQLdb
except ImportError:
    MySQLdb = None
try:
    import psycopg2
except ImportError:
    psycopg2 = None

MYSQL_TEST_DB_CONNECTION = os.environ.get(
    "MYSQL_TEST_DB_CONNECTION", "mysql://root@localhost/test_db_to_sqlite"
)
POSTGRESQL_TEST_DB_CONNECTION = os.environ.get(
    "POSTGRESQL_TEST_DB_CONNECTION", "postgresql://localhost/test_db_to_sqlite"
)


def all_databases(fn):
    "Decorator which parameterizes test function for mysql and postgresql"
    return pytest.mark.parametrize(
        "connection",
        [
            pytest.param(
                MYSQL_TEST_DB_CONNECTION,
                marks=pytest.mark.skipif(
                    MySQLdb is None, reason="pip install mysqlclient"
                ),
            ),
            pytest.param(
                POSTGRESQL_TEST_DB_CONNECTION,
                marks=pytest.mark.skipif(
                    psycopg2 is None, reason="pip install psycopg2"
                ),
            ),
        ],
    )(fn)
