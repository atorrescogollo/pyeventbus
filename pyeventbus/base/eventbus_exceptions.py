"""
Exceptions for EventBus.
"""


class EventBusError(Exception):
    """
    Base class for EventBus exceptions.
    """


class HandlerAlreadySubscribedError(EventBusError):
    """
    Raised when a handler is already subscribed to an event.
    """


class HandlerNotSubscribedError(EventBusError):
    """
    Raised when a handler is not subscribed to an event.
    """
