from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers.campaign import router as campaign_router
from app.routers.recipient import router as recipient_router
from app.routers.notification import router as notification_router
from app.routers.user import router as user_router
from app.exceptions import AppException


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:  # noqa: U100
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    
    
def create_app() -> FastAPI:
    app = FastAPI()
    
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    
    app.include_router(campaign_router, tags=['campaign'])
    app.include_router(recipient_router, tags=['recipient'])
    app.include_router(notification_router, tags=['notification'])
    app.include_router(user_router, tags=['user'])
    
    return app
