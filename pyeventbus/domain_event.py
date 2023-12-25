"""
Domain event interface.
"""
from abc import ABC
from dataclasses import dataclass


@dataclass
class DomainEvent(ABC):
    """
    Interface for domain events.
    """
