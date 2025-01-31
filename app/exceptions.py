from datetime import datetime

from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, detail: str, status_code: int) -> None:
        self.detail = detail
        self.status_code = status_code
        

class ConflictException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)
    

class NotFoundException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class LaunchDateException(AppException):
    def __init__(self, launch_date: datetime) -> None:
        super().__init__(
            detail=f'Launch date [launch_date: {launch_date}] < {datetime.now()} must be in the future',
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    

class NoCampaignsAvailableException(AppException):
    def __init__(self) -> None:
        super().__init__(
            detail='No campaigns available for launch',
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    
class WorkerException(AppException):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail=detail, status_code=status_code)


class EmailSendException(AppException):
    def __init__(self, campaign_id: int, email: str) -> None:
        super().__init__(
            detail=f'mail sending error: [{campaign_id}: {email}]', 
            status_code=status.HTTP_424_FAILED_DEPENDENCY
        )


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
