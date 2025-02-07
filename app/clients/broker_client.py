import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

from app.config import Config


class RabbitMQClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.connection: AbstractRobustConnection | None = None
        # TODO AlexP: Подумать что сделать аннотацией
        self.channel: AbstractChannel = None   # type: ignore
               
    async def connect(self) -> None:
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.config.RABBIT_MQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)    

    async def get_channel(self) -> AbstractChannel:
        if not self.channel:
            await self.connect()
        return self.channel
