from datetime import datetime


class AppException(Exception):
    def __init__(self, detail: str, status_code: int) -> None:
        self.detail = detail
        self.status_code = status_code
        

class ConflictException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=409)
    

class NotFoundException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=404)


class LaunchDateException(AppException):
    def __init__(self, launch_date: datetime) -> None:
        super().__init__(
            detail=f'Launch date [launch_date: {launch_date}] < {datetime.now()} must be in the future',
            status_code=422
        )
    

class NoCampaignsAvailableException(AppException):
    def __init__(self) -> None:
        super().__init__(detail='No campaigns available for launch', status_code=422)
    
    
class WorkerException(AppException):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail=detail, status_code=status_code)


class EmailSendException(AppException):
    def __init__(self, campaign_id: int, email: str) -> None:
        super().__init__(detail=f'email send error: [{campaign_id}: {email}]', status_code=424)
