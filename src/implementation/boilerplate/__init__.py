""" This module provides the entrypoint to the boilerplate logging library.

Provides the following decorators:

- @log
- @log(channel_name: str)
"""


import functools
import logging
import sys
from typing import List, Callable, AnyStr, Union
from types import FunctionType

__name__ = "boilerplate"
__version_info__ = (0, 0, 1)
__version__ = ".".join(map(str, __version_info__))

ACCEPTABLE_CHANNELS = ["inputs", "outputs", "all"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

statikmethodtype = type(staticmethod(len))
klassmethodtype = type(classmethod(len))


@functools.singledispatch
def log(channels: Union[List[AnyStr], str] = []) -> Callable:
    """ Activate one or more channels of boilerplate logging.

    Credit to: t.dubrownik
    Source: https://stackoverflow.com/questions/5929107
    """
    if isinstance(channels, str):
        channels = [channels]
    elif not isinstance(channels, list):
        raise ValueError(f"'channels' must be a list of strings, not '{type(channels)}'.")
    elif len(channels) == 0:
        channels = ["inputs", "outputs"]

    unacceptable_channels = [x for x in channels if x not in ACCEPTABLE_CHANNELS]
    if len(unacceptable_channels) > 0:
        message = f"The following channels are unacceptable: {unacceptable_channels}."
        message += "See: boilerplate.ACCEPTABLE_CHANNELS for acceptable channels."
        raise ValueError(message)

    def layer(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(func, (statikmethodtype, klassmethodtype)):
                message = "You have decorated a staticmethod or a classmethod *decorator*, "
                message += "which is not functional behavior. "
                message += "You probably meant to apply this decorator to the method itself. "
                message += "Switch the order of the decorators and ensure the 'log' decorator is "
                message += "the closest to the method definition."
                raise ValueError(message)

            pf = f'{func.__module__}.{getattr(func, "__qualname__", "__name__")}'

            if "inputs" in channels:
                logger.debug(f"[{pf}] inputs: [args: {args}] [kwargs: {kwargs}]")

            retval = func(*args, **kwargs)
            if "outputs" in channels:
                logger.debug(f"[{pf}] returns: [{retval}]")
            return retval

        return wrapper

    return layer


@log.register(FunctionType)
def _(func: Callable) -> Callable:
    """ Invoke bp.log without arguments.

    Single dispatch generic type for bp.log.
    Simple version of bp.log -- defaults to logging inputs and outputs.
    Specific override for functions.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(func, (statikmethodtype, klassmethodtype)):
            message = "You have decorated a staticmethod or a classmethod *decorator*, "
            message += "which is not functional behavior. "
            message += "You probably meant to apply this decorator to the method itself. "
            message += "Switch the order of the decorators and ensure the 'log' decorator is "
            message += "the closest to the method definition."
            raise ValueError(message)

        pf = f'{func.__module__}.{getattr(func, "__qualname__", "__name__")}'

        logger.debug(f"[{pf}] inputs: [args: {args}] [kwargs: {kwargs}]")
        retval = func(*args, **kwargs)
        logger.debug(f"[{pf}] returns: [{retval}]")
        return retval

    return wrapper
