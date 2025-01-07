import asyncio
import logging
from collections.abc import Coroutine
from typing import Callable, Optional, Self

from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription

logger = logging.getLogger('stdout')


class NatsClient:
    def __init__(self, url: str = 'nats://localhost:4222'):
        self.connect = Client()
        self.url = url

    async def connection(self) -> Self:
        await self.connect.connect(self.url)
        return self

    async def close(self):
        logger.info('Closing connection')
        await self.connect.close()

    async def publish(self, subject: str, message: bytes):
        logger.info(f"Publishing message on '{subject}': {message}")
        await self.connect.publish(subject, message)
        await self.connect.flush()

    async def _callback(self, msg: Msg):
        logger.info(f"Received a message on '{msg.subject}': {msg.data.decode()}")
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Print Received a message on '{subject=} {reply=}': {data=}")

    async def subscribe(self, subject: str) -> Subscription:
        return await self.connect.subscribe(subject, cb=self._callback)

    async def unsubscribe(self, subscription: Subscription, limit: int = 0):
        await subscription.unsubscribe(limit=limit)

    async def terminate(self):
        await self.connect.drain()

    async def __aenter__(self) -> Self:
        return await self.connection()

    async def __aexit__(self, exc_type, exc, tb):
        try:
            pass
        except Exception:
            pass
        finally:
            await self.connect.close()


class NatsConnection:
    __slots__ = ('connect', 'url')

    def __init__(self, url: str = 'nats://localhost:4222'):
        self.connect = Client()
        self.url = url

    async def to_connect(self) -> Client:
        await self.connect.connect(self.url)
        return self.connect

    async def close(self):
        logger.info('Closing connection')
        await self.connect.close()

    async def terminate(self):
        await self.connect.drain()

    @staticmethod
    def run_async(coro: Coroutine):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
        except RuntimeError as e:
            logger.exception(f'Error: {e}')

    def __enter__(self) -> Self:
        self.run_async(self.to_connect())
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            pass
        except Exception:
            pass
        finally:
            self.run_async(self.connect.close())

    async def __aenter__(self) -> Self:
        await self.to_connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            pass
        except Exception:
            pass
        finally:
            await self.connect.close()


class NatsSabscriber:
    def __init__(self, public: str, connect: Client):
        self.public: str = public
        self.connect: Client = connect
        self.subscription: Subscription = None

    async def callback(self, msg: Msg):
        logger.info(f"Received a message on '{msg.subject}': {msg.data.decode()}")
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Print Received a message on '{subject=} {reply=}': {data=}")

    async def subscribe(self, callback: Optional[Callable] = None) -> Subscription:
        if callback is None:
            callback = self.callback
        self.subscription = await self.connect.subscribe(self.public, cb=callback)
        logger.info(f'Subscribed to topic: {self.public}')

    async def unsubscribe(self, limit: int = 0):
        if self.subscription is None:
            raise Exception('Subscription not found')
        await self.subscription.unsubscribe(limit=limit)


class NatsPublisher:
    __slots__ = ('public', 'connect')

    def __init__(self, public: str, connect: Client):
        self.public: str = public
        self.connect: Client = connect
        logger.info(f'Public subject: {self.public}')

    async def publish(self, message: bytes):
        await self.connect.publish(self.public, message)
        await self.connect.flush()


async def test_nats_client():
    public = 'public_test'

    async def subscriber():
        async with NatsClient() as client:
            sub = await client.subscribe(public)
            # Wait for all messages to be received
            await asyncio.sleep(3)

    async def publisher():
        async with NatsClient() as client:
            for i in range(10):
                await client.publish(public, f'Hello World {i}!'.encode())
                # await asyncio.sleep(1)

    await asyncio.gather(publisher(), subscriber())


async def test_nats_context():
    async with NatsConnection() as nats:

        async def subscriber():
            subscriber = NatsSabscriber('public_test', nats.connect)
            await subscriber.subscribe()
            await subscriber.unsubscribe(limit=20)

        async def publisher():
            publisher = NatsPublisher('public_test', nats.connect)
            for i in range(10):
                await publisher.publish(f'Hello World {i}!'.encode())

        await asyncio.gather(publisher(), subscriber())


def test_nats_sync_context():
    async def send_to_broker(public: str):
        async with NatsConnection() as nats:

            async def subscriber():
                subscriber = NatsSabscriber('public_test', nats.connect)
                await subscriber.subscribe()
                await subscriber.unsubscribe(limit=20)

            async def publisher():
                publisher = NatsPublisher('public_test', nats.connect)
                for i in range(10):
                    await publisher.publish(f'Hello World {i}!'.encode())

            await asyncio.gather(publisher(), subscriber())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # asyncio.run(send_to_broker("public_test"))
        asyncio.run_coroutine_threadsafe(send_to_broker('public_test'), loop=loop)
    except KeyboardInterrupt:
        pass


async def test_nats_connection():
    nats = NatsConnection()
    nats_connect = await nats.to_connect()

    async def subscriber():
        subscriber = NatsSabscriber('public_test', nats_connect)
        await subscriber.subscribe()
        await subscriber.unsubscribe(limit=20)
        # await asyncio.sleep(10)

    async def publisher():
        publisher = NatsPublisher('public_test', nats_connect)
        for i in range(10):
            await publisher.publish(f'Hello World {i}!'.encode())
            # await asyncio.sleep(1)

    await asyncio.gather(publisher(), subscriber())


if __name__ == '__main__':
    # asyncio.run(test_nats_client())
    test_nats_sync_context()
    # asyncio.run(test_nats_connection())
    # asyncio.run(test_nats_context())
