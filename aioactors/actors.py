import uuid
import logging
import asyncio
from abc import ABCMeta, abstractmethod

__all__ = ['Inbox', 'Actor']


class Inbox(metaclass=ABCMeta):
    def __init__(self, logger=None, missing=None):
        ''' __init__
        '''
        self.missing = missing
        self.logger = logger if isinstance(logger, logging.Logger) else logging.getLogger(type(self).__name__)

    @abstractmethod
    def get(self):
        ''' get data from inbox
        '''
        raise NotImplementedError()

    @abstractmethod
    def put(self, message):
        ''' put message to inbox
        '''
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        ''' return length of inbox
        '''
        raise NotImplementedError()

    def is_missing(self, item):
        return item is self.missing


class Actor(metaclass=ABCMeta):
    def __init__(self, name=None, logger=None, allow_output=None, timeout=None):
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.allow_output = allow_output if isinstance(allow_output, bool) else getattr(self, 'allow_output', False)
        self.timeout = timeout if isinstance(timeout, int) else getattr(self, 'timeout', 0.01)

        self._name = name if name else self.__class__.__name__
        self._waiting = False
        self._processing = False

        self.address = uuid.uuid4().hex
        self.parent = None
        self.inbox_init()

    def inbox_init(self):
        self.inbox = Inbox()

    def __str__(self):
        ''' represent actor as string '''
        return u'{}[{}]'.format(self._name, self.address)

    @property
    def name(self):
        ''' property get actor name '''
        return self._name

    @property
    def waiting(self):
        ''' propery get waiting for new messages '''
        return self._waiting

    @waiting.setter
    def waiting(self, value):
        ''' propery set waiting for new messages '''
        if isinstance(value, bool):
            self._waiting = value
        else:
            raise RuntimeError('Incorrect waiting type, {}. It must be boolean'.format(type(value)))

    @property
    def processing(self):
        ''' property get actor porcessing status '''
        return self._processing

    @processing.setter
    def processing(self, value):
        ''' property set actor porcessing status '''
        if isinstance(value, bool):
            self._processing = value
        else:
            raise RuntimeError('Incorrect processing type, {}. It must be boolean'.format(type(value)))

    @property
    def is_waiting_message(self):
        """ Override """
        return True

    def start(self):
        ''' start actor
        '''
        self.waiting = False
        self.processing = True

        ioloop = asyncio.get_event_loop()
        ioloop.create_task(self.run())
        try:
            ioloop.run_forever()
        except Exception as e:
            print(e)
            self.stop()

    def stop(self):
        ''' stop actor and its children
        '''
        self.processing = False
        self.waiting = False

    async def run(self):
        ''' run actor
        '''
        self.processing = True
        while True:
            try:
                await self.run_once()
            except Exception as e:
                raise e
                break

    async def run_once(self):
        ''' run actor for one iteraction (used by GeneratorActor and GreenletActor)
        '''
        self.processing = True
        return await self.loop()

    def send(self, **message):
        ''' send message to actor
        '''
        overwrite = message.pop('overwrite') if isinstance(message.get('overwrite'), bool) else False
        allow_parent = message.pop('allow_parent') if isinstance(message.get('allow_parent'), bool) else False
        message = dict() if not isinstance(message, dict) else message

        if self.message and not overwrite:
            data = self.message.copy()
            data.update(message)
        else:
            data = message

        if self.steps:
            steps = self.steps[:]
            next_class = steps.pop(0)
            data['steps'] = steps

            actors = self.find(actor_class=next_class)
            if not actors:
                error_message = dict(message=u"Coudn't find next target in system: {0}".format(next_class))
                error_message.update(dict(sid=data.get('ssid'))) if 'ssid' in data else None
                error_message.update(dict(sid=data.get('mid'))) if 'mid' in data else None
                self.error(**error_message)

            for actor in actors:
                self.logger.debug("<{0}> - Send Message: {{{1}}} To: {2}".format(self, data.keys(), actor))
                actor.inbox.put(data)
                actor.start()
        elif self.parent and (allow_parent or self.allow_parent):
            self.parent.send(data)
        else:
            self.logger.debug(u"<{0}> - Send To Next: {1}".format(self, data))

        self.sleep()

    def error(self, message=None, **kwargs):
        self.logger.error(u"<{0}> - Got Error: {1}".format(self, message))
        allow_parent = kwargs.pop('allow_parent') if isinstance(kwargs.get('allow_parent'), bool) else False

        if (allow_parent or self.allow_parent):
            out = {'result': False, 'error': message}

            if self.message and self.message.get('ssid', None):
                out.update(dict(ssid=self.message.get('ssid')))

            if self.message and self.message.get('mid', None):
                out.update(dict(mid=self.message.get('mid')))
            out.update(kwargs)

            self.parent.send(out)
        self.stop()

    async def loop(self):
        while self.processing:
            self.message = self.inbox.get()
            if self.inbox.is_missing(self.message) and self.is_waiting_message:
                await self.sleep()
                break

            self._parse()
            if self.validate():
                await self.process()

        self.end()

    def _parse(self):
        if self.message and self.message.get('steps', None):
            self.steps = self.message.get('steps')
        return self.parse()

    def end(self):
        """ Override """
        self.steps = list()
        self.message = None
        self.sleep() if len(self.inbox) > 0 else self.stop()

    def sleep(self, timeout=None):
        timeout = timeout if isinstance(timeout, int) else self.timeout
        return asyncio.sleep(timeout)

    @abstractmethod
    def parse(self):
        """ Override """
        raise NotImplementedError()

    @abstractmethod
    def validate(self):
        """ Override """
        raise NotImplementedError()

    @abstractmethod
    def process(self):
        """ Override """
        raise NotImplementedError()
