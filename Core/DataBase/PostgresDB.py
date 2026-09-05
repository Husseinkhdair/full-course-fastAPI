from Core import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = Settings()

engine = create_engine(settings.postgre_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)