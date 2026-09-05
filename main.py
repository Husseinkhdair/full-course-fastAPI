from contextlib import asynccontextmanager
from Core.security.Middleware import middlewareApp
from fastapi import FastAPI
from Core.logging_config import setup_logging
from Features.Auth.Presentation.route import router as auth_router
from Core.DataBase.PostgreDB import get_postgres_pool, init_postgres_db, close_postgres_pool
import logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing PostgreSQL database tables if needed...")
        pool = await get_postgres_pool()
        await init_postgres_db(pool)
    except Exception as e:
        logger.warning(f"PostgreSQL startup initialization warning: {e}")
    yield
    try:
        await close_postgres_pool()
    except Exception:
        pass


app = FastAPI(lifespan=lifespan)

app.middleware("http")(middlewareApp)

app.include_router(auth_router)

@app.get('/')
def read_root():
    logger.info("Test Log")
    return {'Hello': 'World'}




