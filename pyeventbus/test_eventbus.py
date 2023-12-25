"""
Tests for the eventbus class.
"""

from dataclasses import dataclass, field

import pytest

from pyeventbus.domain_event import DomainEvent
from pyeventbus.eventbus import EventBus


@dataclass
class DemoEventBus(EventBus):
    """
    A demo event bus.
    """

    def publish(self, event: DomainEvent) -> None:
        """
        Publishes an event to the bus.
        """


@pytest.fixture(name="eventbus")
def fixture_eventbus() -> DemoEventBus:
    """
    Returns a new DemoEventBus instance.
    """
    return DemoEventBus()


@dataclass
class DemoEvent1(DomainEvent):
    """
    A demo event.
    """

    value1: int


@dataclass
class DemoEvent2(DomainEvent):
    """
    A demo event.
    """

    value2: str


@dataclass
class Handler1:
    """
    A demo handler.
    """

    eventbus: EventBus
    calls: list[int] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.eventbus.subscribe(
            DemoEvent1, lambda event: self.handle(event.value1), self.__class__
        )

    def handle(self, input1: int) -> None:
        """
        Handles an event.
        """
        print(f"Handler1 called with {input1}")
        self.calls.append(input1)


@dataclass
class Handler2:
    """
    A demo handler.
    """

    eventbus: EventBus
    calls: list[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.eventbus.subscribe(
            DemoEvent1,
            lambda event: self.handle(str(event.value1)),
            self.__class__,
        )
        self.eventbus.subscribe(
            DemoEvent2,
            lambda event: self.handle(event.value2),
            self.__class__,
        )

    def handle(self, input2: str) -> None:
        """
        Handles an event.
        """
        print(f"Handler1 called with {input2}")
        self.calls.append(input2)


def test_subscriptions(eventbus: DemoEventBus) -> None:
    """
    Tests that multiple handlers are retrieved
    """
    handler1 = Handler1(eventbus)  # Automatically subscribes to DemoEvent1
    handler2 = Handler2(
        eventbus
    )  # Automatically subscribes to DemoEvent1 and DemoEvent2
    assert eventbus.get_handlers(DemoEvent1) == [
        handler1.__class__,
        handler2.__class__,
    ], "Subscriptions are not retrieved correctly"
    assert eventbus.get_handlers(DemoEvent2) == [
        handler2.__class__
    ], "Subscriptions are not retrieved correctly"


def test_call_handler(eventbus: DemoEventBus) -> None:
    """
    Tests that a handler is called
    """
    handler1 = Handler1(eventbus)  # Automatically subscribes to DemoEvent1
    handler2 = Handler2(
        eventbus
    )  # Automatically subscribes to DemoEvent1 and DemoEvent2

    handlers = eventbus.get_handlers(DemoEvent1)
    assert handlers == [
        handler1.__class__,
        handler2.__class__,
    ], "Handler is not subscribed"
    for handler in handlers:
        eventbus.call_handler(DemoEvent1(1), handler)

    handlers = eventbus.get_handlers(DemoEvent2)
    assert handlers == [handler2.__class__], "Handler is not subscribed"
    eventbus.call_handler(DemoEvent2("a"), handlers[0])

    assert handler1.calls == [1], "Handler1 is not called"
    assert handler2.calls == ["1", "a"], "Handler2 is not called"
