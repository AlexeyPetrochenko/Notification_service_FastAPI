class AppException(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
    
    
class WorkerException(AppException):
    def __init__(self, status_code: int, reason) -> None:
        super().__init__(reason=reason)
        self.status_code = status_code


class EmailSendException(AppException):
    def __init__(self, campaign_id: int, email: str) -> None:
        super().__init__(reason=f'email send error: [{campaign_id}: {email}]')
