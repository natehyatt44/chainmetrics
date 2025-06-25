import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 3),
                }
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "process_time": round(process_time, 3),
                }
            )
            
            raise


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware for setting cache control headers."""
    
    def __init__(self, app, cache_max_age: int = 300):
        super().__init__(app)
        self.cache_max_age = cache_max_age
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Set cache headers for GET requests
        if request.method == "GET" and response.status_code == 200:
            if "/current" in str(request.url):
                # Short cache for current data
                response.headers["Cache-Control"] = f"public, max-age=60"
            elif "/history" in str(request.url):
                # Longer cache for historical data
                response.headers["Cache-Control"] = f"public, max-age={self.cache_max_age}"
            elif "/stats" in str(request.url):
                # Medium cache for stats
                response.headers["Cache-Control"] = f"public, max-age=180"
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response