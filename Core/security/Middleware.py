import time
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from Core.logging_config import request_id_var, user_id_var
from Core.security.Jwt import verify_token
from Core.errors.AuthErrors import InvalidToken

logger = logging.getLogger('Middleware.py')

async def middlewareApp(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_token = request_id_var.set(request_id)
    user_id_token = None

    path = request.url.path
    method = request.method

    # 1. Extract token from Authorization header or cookies if present
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        else:
            token = auth_header.strip()
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    # 2. If token is present, verify its validity
    if token:
        try:
            payload = verify_token(token)
            if payload and payload.id:
                user_id_token = user_id_var.set(str(payload.id))
        except (InvalidToken, Exception) as e:
            duration = round((time.time() - start_time) * 1000, 2)
            logger.warning("Request rejected: Invalid token", extra={
                "path": path,
                "method": method,
                "duration": f"{duration}ms",
                "error": str(e)
            })
            response = JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
            response.headers["X-Request-ID"] = request_id
            request_id_var.reset(request_id_token)
            return response

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
        if user_id_token is not None:
            user_id_var.reset(user_id_token)


