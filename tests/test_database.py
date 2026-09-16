from sqlalchemy import text

from src.utils.database import engine


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