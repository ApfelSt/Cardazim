from __future__ import annotations
from abc import ABC, abstractmethod
from card import Card


class CardDriver(ABC):
    @abstractmethod
    def save(self, metadata: dict[str, str], identifier: str) -> None:
        """Save the card data associated with the identifier."""
        pass

    @abstractmethod
    def get_identifier(self, name: str, creator: str) -> str:
        """Get the unique identifier for the card with the given name and creator."""
        pass

    @abstractmethod
    def load(self, identifier: str) -> dict[str, str]:
        """Load the card data associated with the identifier."""
        pass

    @abstractmethod
    def get_creators(self) -> list[str]:
        """Return a list of available card creators."""
        pass

    @abstractmethod
    def get_creator_cards(self, creator: str) -> list[dict[str, str]]:
        """Return a list of card names created by the specified creator."""
        pass

    @abstractmethod
    def get_creator_card_names(self, creator: str) -> list[str]:
        """Return a list of card names created by the specified creator."""
        pass
