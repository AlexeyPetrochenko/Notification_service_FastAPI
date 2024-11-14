from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import typing as t

from app.routers.campaign import router as campaign_router
from app.routers.recipient import router as recipient_router
from app.routers.notification import router as notification_router
from app.exceptions import AppException


def config_logging() -> None:
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(levelname)s:   %(asctime)s - %(message)s',
    )


def get_logger() -> logging.Logger:
    return logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: t.Callable) -> Response:
        logger = get_logger()
        response = await call_next(request)
        logger.info(f'"{request.method} {request.url}" {response.status_code}')
        return response


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:  # noqa: U100
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    
    
def create_app() -> FastAPI:
    app = FastAPI()
    
    config_logging()
    app.add_middleware(LoggingMiddleware)
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    
    app.include_router(campaign_router, tags=['campaign'])
    app.include_router(recipient_router, tags=['recipient'])
    app.include_router(notification_router, tags=['notification'])
    
    return app
