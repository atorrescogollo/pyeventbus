# PyEventBus
EventBus implementations in Python. It allows you to easily publish custom domain events and subscribe commands to them.

## Installation
```bash
pip install python3-eventbus
```

## AWS
### SNSEventBus
This implementation will forward events to an AWS SNS topic. The topic must be created before the event bus is used.

You can see and example of how to use it in the `examples` folder: [aws_sns.ipynb](./examples/aws_sns.ipynb)
