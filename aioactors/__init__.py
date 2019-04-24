import asyncio
from logging import getLogger
from abc import abstractmethod, ABC

__version__ = "1.0"
__doc__ = "Simple abstractions for actor model based on asyncio"

TASK_TIMEOUT = 5


class Actor(ABC):
    def __init__(self, **kwargs) -> None:
        self.logger = getLogger(type(self).__name__)
        if '_id' in kwargs:
            self.id = kwargs['_id']
            self.logger = getLogger(f"{type(self).__name__}.{self.id}")

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

    def __call__(self):
        try:
            self.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def start(self) -> None:
        self.logger.info("Starting...")
        self.loop.run_forever()

    def stop(self) -> None:
        self.logger.info("Stopping...")

        for task in asyncio.Task.all_tasks():
            self.logger.info("Stop '{}'".format(task))
            task.cancel()

        self.logger.info("Stop mainloop")
        self.loop.stop()
        self.loop.close()

    def add(self, task: Actor, timeout: int = TASK_TIMEOUT):
        return asyncio.ensure_future(task.start(timeout))
