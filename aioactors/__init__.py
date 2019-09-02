import typing as t

import asyncio
from logging import getLogger
from abc import abstractmethod, ABC

__version__ = "1.1.0"
__doc__ = "Simple abstractions for actor model based on asyncio"

TASK_TIMEOUT = 5


class Actor(ABC):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.logger = getLogger(cls.__name__)
        if '_id' in kwargs:
            obj.id = kwargs['_id']
            obj.logger = getLogger(f"{cls.__name__}.{obj.id}")
        return obj

    @abstractmethod
    async def __call__(self) -> None:
        raise NotImplementedError()

    async def start(self, timeout: int = TASK_TIMEOUT) -> None:
        while True:
            await self()
            await asyncio.sleep(timeout)


class ActorSystem(object):
    def __init__(self, loop) -> None:
        self.logger = getLogger(type(self).__name__)
        self.loop = loop

        self.tasks: t.List[asyncio.Coroutine] = list()

    def __call__(self):
        try:
            self.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def start(self) -> None:
        self.logger.info("Starting...")
        self.loop.run_until_complete(asyncio.gather(*self.tasks))

    def stop(self) -> None:
        self.logger.info("Stopping...")

        for task in asyncio.Task.all_tasks():
            self.logger.info("Stop '{}'".format(task))
            task.cancel()

        self.logger.info("Stop mainloop")
        self.loop.stop()
        self.loop.close()

    def add(self, task: Actor, timeout: int = TASK_TIMEOUT):
        self.tasks.append(task.start(timeout))
