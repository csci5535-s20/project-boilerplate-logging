""" Provides the entrypoint to the boilerplate logging library.

Provides the following decorators:

- @log
- @log(channel_name: str)
"""


import functools
import logging
import os
import sys
import collections

from typing import List, Callable, AnyStr, Union
from types import FunctionType

__name__ = "boilerplate"
__version_info__ = (0, 0, 2)
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


trace_queue = collections.deque(maxlen=os.getenv("BOILERPLATE_TRACE_MAXLEN", 10))

# PUBLIC INTERFACE #############


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
            _validate_type(func)

            if "inputs" in channels:
                logger.debug(_format_input(func, args, kwargs))

            retval = func(*args, **kwargs)
            if "outputs" in channels:
                logger.debug(_format_output(func, retval))
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
        _validate_type(func)

        logger.debug(_format_input(func, args, kwargs))
        retval = func(*args, **kwargs)
        logger.debug(_format_output(func, retval))
        return retval

    return wrapper


def register_uncaught_exception_handler() -> None:
    """ Register boilerplate as the uncaught exception handler.

    Will flush trace logs to boilerplate.logger before calling the original excepthook.
    """
    global original_hook
    original_hook = sys.excepthook
    sys.excepthook = _uncaught_exception_handler
    logger.debug("Registered as uncaught exception handler!")


def unregister_uncaught_exception_handler() -> None:
    """ Unregister boilerplate as the uncaught exception handler.

    Replaces sys.excepthook with whatever it was before .register_uncaught_exception_handler()
    was called.
    """
    # Should maybe replace with original sys.__excepthook__ if can't replace for whatever reason.
    # Source: https://docs.python.org/3/library/sys.html#sys.__excepthook__
    # Caller *could* have their own except hook theoretically.
    # Be a good citizen and replace it.
    global original_hook
    sys.excepthook = original_hook
    logger.debug("Unregistered as uncaught exception handler.")


def _uncaught_exception_handler(*exc_info):
    global original_hook
    logger.debug("Exception occurred; flushing boilerplate trace.")
    flush()
    original_hook(*exc_info)


def trace(func: Callable) -> Callable:
    """ Register the wrapped function to be traced. """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _validate_type(func)
        trace_queue.appendleft(_format_input(func, args, kwargs))
        retval = func(*args, **kwargs)
        trace_queue.appendleft(_format_output(func, retval))
        return retval

    return wrapper


def flush() -> None:
    """ Flush any current boilerplate trace statements to log. """
    logger.debug("== BOILERPLATE TRACE:")
    while len(trace_queue) > 0:
        try:
            msg = trace_queue.pop()
        except IndexError:
            break
        else:
            logger.debug(msg)
    logger.debug("== END BOILERPLATE TRACE ==")


# PRIVATE INTERFACE #############


def _validate_type(func: Callable) -> None:
    if isinstance(func, (statikmethodtype, klassmethodtype)):
        message = "You have decorated a staticmethod or a classmethod *decorator*, "
        message += "which is not functional behavior. "
        message += "You probably meant to apply this decorator to the method itself. "
        message += "Switch the order of the decorators and ensure the 'log' decorator is "
        message += "the closest to the method definition."
        raise ValueError(message)


def _format_prefix(func):
    pf = f'{func.__module__}.{getattr(func, "__qualname__", "__name__")}'
    return pf


def _format_input(func, args, kwargs):
    return f"[{_format_prefix(func)}] inputs: [args: {args}] [kwargs: {kwargs}]"


def _format_output(func, retval):
    return f"[{_format_prefix(func)}] returns: [{retval}]"
