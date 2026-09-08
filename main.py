import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from Core.logging_config import setup_logging
from Core.security.Middleware import middlewareApp
from Features.Auth.Presentation.route import router as auth_router

# Step 1: Initialize logging
setup_logging()

# Step 2: Logger resolution
logger = logging.getLogger(__name__)

# Step 3: FastAPI instantiation
app = FastAPI(
    title="FastAPI Auth & User System",
    description="Clean Architecture REST API with Modern Web Dashboard",
    version="1.0.0"
)

# Step 4: HTTP Middleware Registration
app.middleware("http")(middlewareApp)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 5: Feature Router Mounting
app.include_router(auth_router)

# Mount Web frontend static files
web_dir = os.path.join(os.path.dirname(__file__), "Web")
if os.path.isdir(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")







