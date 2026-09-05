from Core.security.Middleware import middlewareApp
from fastapi import FastAPI
from Core.logging_config import setup_logging
from Features.Auth.Presentation.route import router as auth_router
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

app.middleware("http")(middlewareApp)

app.include_router(auth_router)

@app.get('/')
def read_root():
    logger.info("Test Log")
    return {'Hello': 'World'}




