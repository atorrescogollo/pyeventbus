"""
Module for SNS event bus.
"""
import json
import logging
import typing
from dataclasses import dataclass

from pyeventbus.base.domain_event import DomainEvent
from pyeventbus.base.eventbus import EventBus

SNSTopic = typing.Any
if typing.TYPE_CHECKING:
    from mypy_boto3_sns.service_resource import Topic as SNSTopic

logger = logging.getLogger(__name__)


@dataclass
class SNSEventBus(EventBus):
    """
    Implementation of event bus using SNS.
    """

    sns_topic: SNSTopic

    def publish(self, event: DomainEvent) -> None:
        logger.debug("Publishing event %s to SNS topic %s", event, self.sns_topic)
        self.sns_topic.publish(
            Message=json.dumps(
                {
                    "event_type": event.__class__.__name__,
                    "event": event.to_dict(),
                }
            ),
        )
