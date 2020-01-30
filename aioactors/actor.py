import asyncio
from logging import getLogger, Logger
from abc import abstractmethod, ABC

from .constants import DEFAULT_TASK_TIMEOUT


class Actor(ABC):
    logger: Logger = None

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)

        if not isinstance(obj.logger, Logger):
            obj.logger = getLogger(cls.__name__)

        if '_id' in kwargs:
            obj.id = kwargs['_id']
            obj.logger = obj.logger.getChild(str(obj.id))

        return obj

    @abstractmethod
    async def __call__(self) -> None:
        raise NotImplementedError()

    async def start(self, timeout: int = DEFAULT_TASK_TIMEOUT) -> None:
        while True:
            await self()
            await asyncio.sleep(timeout)
