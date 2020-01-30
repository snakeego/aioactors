from __future__ import annotations
import typing as t

from logging import Logger

T = t.TypeVar('T')


def base_logger(logger: Logger):
    ''' Setup base logger for class '''

    def setup_logger(cls: T) -> T:
        setattr(cls, 'logger', logger.getChild(cls.__name__))
        return cls

    return setup_logger
