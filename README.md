# PyEventBus
EventBus implementations in Python. It allows you to easily publish custom domain events and subscribe commands to them.

## Installation
```bash
pip install python3-eventbus
```

## Usage
1. Create the event bus (see "EventBus types" section for more details)
```python
sender_topic = boto3.resource("sns", region_name="us-east-1").Topic(sns_sender_arn)
eventbus = SNSEventBus(sender_topic)
```

2. Define your event
```python
@dataclass
class UserCreatedEvent(DomainEvent):
    user_id: str

    def to_dict(self) -> dict[str, str]:
        return {"user_id": self.user_id}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls(data["user_id"])
```
3. Define the subscriber
```python
@dataclass
class SendWelcomeEmailCommand:
    eventbus: EventBus

    def __post_init__(self):
        self.eventbus.subscribe(
            UserCreatedEvent, # The event to subscribe to
            lambda event: self.send_welcome_email(event.user_id), # The callback
            self.__class__, # The subscriber entity
        )

    def send_welcome_email(self, user_id: str):
        ...Business logic...
```
4. Register the subscriber
```python
send_welcome_email_command = SendWelcomeEmailCommand(eventbus) # This will execute the __post_init__ method (dataclass feature)
```

5. Publish the event
```python
eventbus.publish(UserCreatedEvent("user_id"))
```

6. From your controller, rebuild the domain event based on the subscriptions
```python
def lambda_handler(event: dict[str, Any], context: Any):
    raw_domain_event = _unwrap_event(event) # Remove event metadata (SQS, SNS, etc.)
    domain_event = eventbus.build_event_from_subscriptions(
        raw_domain_event["event_type"],
        raw_domain_event["event"],
    )
```

## EventBus types
### AWS: SNSEventBus
This implementation will forward events to an AWS SNS topic. The topic must be created before the event bus is used.

```python
sender_topic = boto3.resource("sns", region_name="us-east-1").Topic(sns_sender_arn)
eventbus = SNSEventBus(sender_topic)
```
Complete example: [aws_sns.ipynb](./examples/aws_sns.ipynb)
