import os
import unittest

from app.configs.settings import get_email_settings
from app.sender import Email, EmailSender

settings = get_email_settings()

TEST_EMAIL: str = os.environ.get('TEST_EMAIL', '')


class TestEmailSender(unittest.TestCase):
    def setUp(self):
        self.sender = EmailSender(settings)

    def test_send(self):
        self.assertIsNot(TEST_EMAIL, '')
        email = Email(TEST_EMAIL, 'test message')
        self.sender.send(email)

    def test_send_batch(self):
        self.assertIsNot(TEST_EMAIL, '')
        emails = [Email(TEST_EMAIL, 'test message 1'), Email(TEST_EMAIL, 'test message2')]
        self.sender.send_batch(emails)


if __name__ == '__main__':
    unittest.main()
