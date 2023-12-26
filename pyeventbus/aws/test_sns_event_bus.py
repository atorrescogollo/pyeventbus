"""
Tests for the SNS event bus.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Self

import boto3
import pytest
from moto import mock_sns
from moto.core import DEFAULT_ACCOUNT_ID  # type: ignore
from moto.sns import sns_backends  # type: ignore

from pyeventbus.aws.sns_event_bus import SNSEventBus
from pyeventbus.base.domain_event import DomainEvent
from pyeventbus.base.eventbus import EventBus


def _sent_notifications(topic_arn: str) -> list[Any]:
    # https://docs.getmoto.org/en/latest/docs/services/sns.html
    sns_backend = sns_backends[DEFAULT_ACCOUNT_ID]["us-east-1"]  # type: ignore
    return sns_backend.topics[topic_arn].sent_notifications  # type: ignore


@dataclass
class CustomDomainEvent(DomainEvent):
    """
    Custom domain event.
    """

    a1: str
    a2: int
    a3: bool
    a4: list[str]
    a5: dict[str, str]

    def to_dict(self) -> dict[str, str]:
        return {
            "a1": self.a1,
            "a2": str(self.a2),
            "a3": str(self.a3),
            "a4": ",".join(self.a4),
            "a5": json.dumps(self.a5),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls(
            a1=data["a1"],
            a2=int(data["a2"]),
            a3=bool(data["a3"]),
            a4=data["a4"].split(","),
            a5=json.loads(data["a5"]),
        )


@dataclass
class Handler:
    """
    Handler for the custom domain event.
    """

    eventbus: EventBus
    calls: list[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.eventbus.subscribe(
            CustomDomainEvent,
            self.handle,
            self.__class__,
        )

    def handle(self, event: DomainEvent) -> None:
        """
        Handle the event.
        """
        self.calls.append(event)


def test_publish() -> None:
    """
    Test that the event is published correctly.
    """
    with mock_sns():
        sns_topic = boto3.resource("sns", region_name="us-east-1").create_topic(
            Name="test-topic"
        )

        eventbus = SNSEventBus(sns_topic)
        eventbus.publish(CustomDomainEvent("a1", 2, True, ["a4"], {"a5": "a5"}))

        sent = _sent_notifications(sns_topic.arn)
        assert len(sent) == 1, "Expected 1 notification"
        assert sent[0][1] == json.dumps(
            {
                "event_type": "CustomDomainEvent",
                "event": {
                    "a1": "a1",
                    "a2": "2",
                    "a3": "True",
                    "a4": "a4",
                    "a5": json.dumps({"a5": "a5"}),
                },
            }
        ), "Unexpected notification payload"


def test_build_event() -> None:
    """
    Test that we can build an event from its name and its initialization parameters.
    """
    with mock_sns():
        sns_topic = boto3.resource("sns", region_name="us-east-1").create_topic(
            Name="test-topic"
        )
        eventbus = SNSEventBus(sns_topic)
        _handler = Handler(eventbus)  # Register handler

        assert eventbus.build_event_from_subscriptions(
            "CustomDomainEvent",
            {
                "a1": "a1",
                "a2": "2",
                "a3": "True",
                "a4": "a4",
                "a5": json.dumps({"a5": "a5"}),
            },
        ) == CustomDomainEvent("a1", 2, True, ["a4"], {"a5": "a5"}), "Unexpected event"

        assert (
            eventbus.build_event_from_subscriptions(
                "CustomEventNotRegistered",
                {},
            )
            is None
        ), "Unexpected event"

        with pytest.raises(KeyError):
            eventbus.build_event_from_subscriptions(
                "CustomDomainEvent",
                {},
            )
