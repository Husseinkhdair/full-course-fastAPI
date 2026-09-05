import time
import uuid
import logging
from fastapi import Request
from Core.logging_config import request_id_var, user_id_var

logger = logging.getLogger('Middleware.py')

async def middlewareApp(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_token = request_id_var.set(request_id)

    path = request.url.path
    method = request.method

    try:
        logger.info("Request Received", extra={
            "path": path,
            "method": method
        })
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        
        logger.info("Request Completed", extra={
            "path": path,
            "method": method,
            "status_code": response.status_code,
            "duration": f"{duration}ms"
        })
        return response
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error("Request Failed", extra={
            "path": path,
            "method": method,
            "duration": f"{duration}ms",
            "error": str(e)
        })
        raise e
    finally:
        request_id_var.reset(request_id_token)

