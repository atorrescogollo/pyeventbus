terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "local" {
    path = "./terraform.tfstate"
  }
}

provider "aws" {
  access_key = "test"
  secret_key = "test"
  region = "us-east-1"

  endpoints {
    sts = "http://localhost:8000"
    sns = "http://localhost:8000"
    sqs = "http://localhost:8000"
  }
}

resource "aws_sns_topic" "sender" {
  name = "my-topic"
}

resource "aws_sqs_queue" "receiver" {
  name = "my-queue"
}

resource "aws_sns_topic_subscription" "receiver" {
  topic_arn = aws_sns_topic.sender.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.receiver.arn
}

output "sns_sender_arn" {
  value = aws_sns_topic.sender.arn
}

output "sqs_receiver_url" {
  value = aws_sqs_queue.receiver.url
}
