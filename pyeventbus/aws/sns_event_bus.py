"""
Module for SNS event bus.
"""
import json
import typing
from dataclasses import dataclass

from pyeventbus.base.domain_event import DomainEvent
from pyeventbus.base.eventbus import EventBus

SNSTopic = typing.Any
if typing.TYPE_CHECKING:
    from mypy_boto3_sns.service_resource import Topic as SNSTopic


@dataclass
class SNSEventBus(EventBus):
    """
    Implementation of event bus using SNS.
    """

    sns_topic: SNSTopic

    def publish(self, event: DomainEvent) -> None:
        self.sns_topic.publish(
            Message=json.dumps(
                {
                    "event_type": event.__class__.__name__,
                    "event": event.to_dict(),
                }
            ),
        )

    def build_event_from_subscriptions(
        self, event_type: str, event: dict[str, str]
    ) -> DomainEvent | None:
        """
        Return an event knowing its name and its initialization parameters. This
        avoid having to manually create a lot of if/else statements to build the
        right event when an unknown event is received.
        """
        for event_cls in self.subscriptions:
            if event_cls.__name__ == event_type:
                return event_cls.from_dict(event)
        return None
