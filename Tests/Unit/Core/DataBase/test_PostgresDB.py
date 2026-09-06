from Core.DataBase.PostgresDB import engine
from sqlalchemy import text


def test_postgres_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
