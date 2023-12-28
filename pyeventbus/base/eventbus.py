"""
Module for the EventBus class.
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, cast

from pyeventbus.base.domain_event import DomainEvent
from pyeventbus.base.eventbus_exceptions import (
    HandlerAlreadySubscribedError,
    HandlerNotSubscribedError,
)

logger = logging.getLogger(__name__)


@dataclass
class EventBus(ABC):
    """
    Generic event bus
    """

    subscriptions: dict[
        type[DomainEvent], dict[type[object], Callable[[DomainEvent], Any]]
    ] = field(init=False, default_factory=dict)

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publishes an event to the bus.
        """

    def subscribe[
        TDomainEvent
    ](
        self,
        event_cls: type[TDomainEvent],
        callback: Callable[[TDomainEvent], Any],
        handler_cls: type[object],
    ) -> None:
        """
        Subscribes a handler to an event.
        """
        logger.debug(
            "Subscribing handler %s to event %s with callback %s",
            handler_cls,
            event_cls,
            callback,
        )
        domain_event = cast(type[DomainEvent], event_cls)
        domain_event_callback = cast(Callable[[DomainEvent], Any], callback)
        if handler_cls in self.subscriptions.get(domain_event, {}):
            raise HandlerAlreadySubscribedError(
                f"Handler {handler_cls} is already subscribed to event {domain_event}"
            )

        self.subscriptions.setdefault(domain_event, {})[
            handler_cls
        ] = domain_event_callback

    def call_handler(self, event: DomainEvent, handler_cls: type[object]) -> Any:
        """
        Calls a handler for an event.
        """
        logger.debug("Calling handler %s for event %s", handler_cls, event)
        callback = self.subscriptions.get(type(event), {}).get(handler_cls, None)
        if callback is None:
            raise HandlerNotSubscribedError(
                f"Handler {handler_cls} is not subscribed to event {event}"
            )
        callback(event)

    def get_handlers(self, event_cls: type[DomainEvent]) -> list[type[object]]:
        """
        Returns the handlers for an event.
        """
        return list(self.subscriptions.get(event_cls, {}).keys())

    def build_event_from_subscriptions(
        self, event_type: str, event: dict[str, str]
    ) -> DomainEvent | None:
        """
        Return an event knowing its name and its initialization parameters. This
        avoid having to manually create a lot of if/else statements to build the
        right event when an unknown event is received.
        """
        logger.debug("Building event %s from subscriptions", event_type)
        for event_cls in self.subscriptions:
            if event_cls.__name__ == event_type:
                logger.debug("Building event %s from subscriptions", event_type)
                return event_cls.from_dict(event)
        return None
