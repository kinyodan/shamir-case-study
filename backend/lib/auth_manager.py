# auth_manager.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from lib.utils import verify_token
import logging

EXCLUDED_PATHS = ["/login","/login/", "/sign_up", "/sign_up/"]

async def verify_token_middleware(request: Request, call_next):
    logging.info(f"Request path: {request.url.path}")
    if request.url.path not in EXCLUDED_PATHS:
        token = request.headers.get("Authorization")
        logging.info(f"Authorization header: {token}")
        
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
    
    response = await call_next(request)
    return response