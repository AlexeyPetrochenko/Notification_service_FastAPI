from fastapi import FastAPI, Request, Response
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import typing as t

from app.routers.campaign import router as campaign_router
from app.routers.recipient import router as recipient_router
from app.routers.notification import router as notification_router


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
    
    
def create_app() -> FastAPI:
    app = FastAPI()
    
    config_logging()
    app.add_middleware(LoggingMiddleware)

    app.include_router(campaign_router, tags=['campaign'])
    app.include_router(recipient_router, tags=['recipient'])
    app.include_router(notification_router, tags=['notification'])
    
    return app

app = create_app()