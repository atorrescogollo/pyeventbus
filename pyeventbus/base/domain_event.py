"""
Domain event interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DomainEvent(ABC):
    """
    Interface for domain events.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        """
        Convert the event to a dictionary.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, str]) -> "DomainEvent":
        """
        Create an event from a dictionary.
        """
