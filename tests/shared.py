import pytest

try:
    import MySQLdb
except ImportError:
    MySQLdb = None
try:
    import psycopg2
except ImportError:
    psycopg2 = None


def all_databases(fn):
    "Decorator which parameterizes test function for mysql and postgresql"
    return pytest.mark.parametrize(
        "connection",
        [
            pytest.param(
                "mysql://root@localhost/test_db_to_sqlite",
                marks=pytest.mark.skipif(
                    MySQLdb is None, reason="pip install mysqlclient"
                ),
            ),
            pytest.param(
                "postgresql://localhost/test_db_to_sqlite",
                marks=pytest.mark.skipif(
                    psycopg2 is None, reason="pip install psycopg2"
                ),
            ),
        ],
    )(fn)
