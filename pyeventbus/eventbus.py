"""
Module for the EventBus class.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, cast

from pyeventbus.domain_event import DomainEvent
from pyeventbus.eventbus_exceptions import (
    HandlerAlreadySubscribedError,
    HandlerNotSubscribedError,
)


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
