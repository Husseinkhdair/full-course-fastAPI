from Core.security.Middleware import middlewareApp
from fastapi import FastAPI
from Core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

app.middleware("http")(middlewareApp)

@app.get('/')
def read_root():
    logger.info("Test Log")
    return {'Hello': 'World'}



