import os

import pytest
from sqlalchemy import text

from src.utils.database import engine


RUN_DB_TESTS = os.getenv("RUN_DB_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_DB_TESTS,
    reason=(
        "Live PostgreSQL/PostGIS integration tests are disabled by default. "
        "Set RUN_DB_TESTS=1 after configuring the test database."
    ),
)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_postgis_extension():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT PostGIS_Version()")
        )
        version = result.scalar()

        assert version is not None
        assert version != ""
