import asyncio

from app.broker import NatsConnection, NatsSabscriber
from app.configs.log_settings import get_logger
from app.configs.settings import get_broker_settings, get_email_settings
from app.services import EmailService

logger = get_logger('stdout')
email_settings = get_email_settings()
logger.debug(f'Email settings: {email_settings}')

PUBLIC = get_broker_settings().public


async def recive_emails():
    logger.info('Starting email service')
    email_service = EmailService(email_settings)

    async with NatsConnection() as nats:
        subscriber = NatsSabscriber(PUBLIC, nats.connect)
        await subscriber.subscribe(email_service.callback)
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(recive_emails())
    except KeyboardInterrupt:
        pass
