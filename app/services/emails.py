import logging
import re

from nats.aio.msg import Msg

from app.configs.settings import EmailSettings, get_email_settings
from app.sender import Email, EmailSender

from .models import BrokerEmailMessage

logger = logging.getLogger('stdout')
email_settings = get_email_settings()
logger.debug(f'Email settings: {email_settings}')


class EmailService:
    re_email = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    email_message_template = """Здравствуйте!
    \nВаша расшифровка аудио запроса:
    \n%s
    \nЕсли вы получили это сообщение по ошибке, то сообщите мне по email или в чате.
    """

    def __init__(self, email_settings: EmailSettings):
        self.email_sender = EmailSender(email_settings)

    def send_email(self, emails: list[str], text: str):
        logger.info(f'Sending emails to {emails}')
        g_emails = (Email(email, self.email_message_template % text) for email in emails)
        self.email_sender.execute(g_emails)
        return emails

    def filter_emails(self, emails: str) -> list[str]:
        logger.debug(f'Doing with {emails}')
        return self.re_email.findall(emails)

    async def callback(self, msg: Msg):
        logger.info(f"Received a message on '{msg.subject}': {msg.data.decode()}")
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Print Received a message on '{subject=} {reply=}': {data=}")
        message = BrokerEmailMessage.model_validate_json(data)
        self.send_email(message.emails, message.text_audio)
