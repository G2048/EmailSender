import logging
import smtplib
import ssl
from collections.abc import Sequence
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Self

from app.configs.settings import EmailSettings

logger = logging.getLogger('stdout')


class Email:
    __slots__ = ('subject', 'message', 'email', 'sender')

    def __init__(self, email: str, message: str):
        self.email = email
        self.message = message
        self.subject = 'Email from the bot'  # Theme of the mail

    def create_message(self, sender: str) -> Self:
        msg = MIMEMultipart()
        msg['From'] = formataddr((self.email, sender))
        msg['To'] = self.email  # + ";" + "test@test.com"
        msg['Subject'] = self.subject
        msg['Bcc'] = sender  # Recommended for mass emails
        msg.attach(MIMEText(self.message, 'plain'))
        self.message = msg.as_string()
        logger.debug(f'Email message created: {self.message}')
        return self

    def __str__(self):
        return f'Email: {self.email}\nMessage: {self.message}'

    def __repr__(self):
        return self.__str__()


class EmailSender:
    def __init__(self, settings: EmailSettings):
        self.port = settings.port
        self.host = settings.host
        self.password = settings.password
        self.sender = settings.sender

    def connect(self):
        server = smtplib.SMTP(self.host, self.port)
        _context = ssl.create_default_context()
        server.starttls(context=_context)
        server.login(self.sender, self.password)
        return server

    def quit(self):
        pass

    def __repr__(self):
        return self.__str__()

    def _recive(self, email: Email):
        server = self.connect()
        try:
            server.sendmail(self.sender, email.email, email.message)
        finally:
            server.quit()

    def send(self, email: Email):
        email.create_message(self.sender)
        logger.info(f'Sending email: {email}')
        self._recive(email)

    def send_batch(self, emails: Sequence[Email]):
        """
        Sends emails in a batch
        :param emails: list of emails
        :return:
        """
        g_emails = (email.create_message(self.sender) for email in emails)
        for email in g_emails:
            logger.debug(f'Sending email: {email}')
            self._recive(email)

    def execute(self, emails: Sequence[Email]):
        """For the Action interface compliance"""
        self.send_batch(emails)
