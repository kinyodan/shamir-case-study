# auth_manager.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from lib.utils import verify_token
import logging

EXCLUDED_PATHS = ["/","/login","/login/", "/sign_up", "/sign_up/"]

class VerifyTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        #logging.info(f"Request path: {request.url.path}")
        response = await call_next(request)

        if request.method == "OPTIONS":
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        if request.url.path not in EXCLUDED_PATHS:
            token = request.headers.get("Authorization")
            #logging.info(f"Authorization header: {token}")

            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authorization header missing"},
                )
            
            token = token.split(" ")[1] if " " in token else token
            if not verify_token(token):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token"},
                )
        
        return response