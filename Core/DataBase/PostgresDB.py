from Core.Settings import SettingsApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = SettingsApp()

engine = create_engine(settings.postgre_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)