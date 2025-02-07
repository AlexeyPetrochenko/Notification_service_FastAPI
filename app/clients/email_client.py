import smtplib
from email.message import EmailMessage

from app.schemas import NotificationBody
from app.exceptions import EmailSendException
from app.config import Config


class EmailClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.server: smtplib.SMTP_SSL = self.connect_server()  
        
    def connect_server(self) -> smtplib.SMTP_SSL:
        server = smtplib.SMTP_SSL(host=self.config.EMAIL_HOST, port=self.config.EMAIL_PORT, timeout=30)
        server.login(user=self.config.EMAIL_NAME, password=self.config.EMAIL_PASS)
        return server
        
    def make_message(self, body: NotificationBody) -> EmailMessage:
        msg = EmailMessage()
        msg['From'] = self.config.EMAIL_NAME
        msg['To'] = body.email
        msg['Subject'] = body.last_name 
        welcome_message = f'Уважаемый {body.last_name} {body.first_name}\n'
        msg.set_content(welcome_message + body.content, charset='utf-8')
        return msg
        
    def send_notification(self, body: NotificationBody, message: EmailMessage) -> None:
        try:
            if not self.server:
                self.server = self.connect_server()
            self.server.send_message(msg=message, from_addr=self.config.EMAIL_NAME, to_addrs=body.email)
        except (smtplib.SMTPException, ValueError):
            raise EmailSendException(body.campaign_id, body.email)
