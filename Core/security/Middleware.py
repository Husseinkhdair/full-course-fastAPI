import uuid
from fastapi import Request
from Core.logging_config import request_id_var, user_id_var
import logging

logger = logging.getLogger('Middleware.py')

async def middlewareApp(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_token = request_id_var.set(request_id)

    try:
        logger.info("Request Received")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info("Request Completed")
        return response
    except Exception as e:
        logger.error("Request Failed")
        raise e
    finally:
        request_id_var.reset(request_id_token)
