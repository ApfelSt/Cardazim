from __future__ import annotations
from card import Card
from os import PathLike
from typing import Generator, Union
import json
import pathlib
import os

IMG_PATH = "image.jpg"
META_PATH = "metadata.json"


class CardManager:
    @staticmethod
    def _generate_identifier() -> Generator[str, None, None]:
        """generate unique identifiers as strings, starting from '0' and incrementing by 1"""
        id = 0
        while True:
            yield str(id)
            id += 1

    @staticmethod
    def _card_dir_name(name: str, creator: str, identifier: str = "") -> str:
        """generate the directory name for a card based on its name and creator"""
        return f"{creator}_{name}_{identifier}"

    @staticmethod
    def _to_path(*args: Union[str, PathLike]) -> str:
        """create a file path by joining given parts"""
        return os.path.join(*map(str, args))

    def __init__(self, storage_dir: Union[str, PathLike]) -> None:
        """self.cards: card creator -> card name -> card id"""
        self.storage_dir = pathlib.Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cards: dict[str, dict[str, str]] = {}
        self._id_generator = self._generate_identifier()

    def get_identifier(self, card: Card) -> str:
        """get or create a unique identifier for the given card.
        If the card already exists, return its existing identifier."""
        name = card.name
        creator = card.creator
        identifier = CardManager._card_dir_name(name, creator)

        if creator in self.cards and name in self.cards[creator]:
            return identifier + self.cards[creator][name]

        new_id = next(self._id_generator)
        if creator not in self.cards:
            self.cards[creator] = {}

        self.cards[creator][name] = new_id
        return identifier + new_id

    def _get_metadata(self, card: Card, image_path: Union[str, PathLike]) -> dict:
        """get metadata dictionary for the given card"""
        metadata = {
            "name": card.name,
            "creator": card.creator,
            "riddle": card.riddle,
            "solution": card.solution,
            "image_path": str(image_path),
        }
        return metadata

    def save(self, card: Card) -> None:
        """save the given card to the storage directory"""
        identifier = self.get_identifier(card)
        card_dir = f"{self.storage_dir}/{identifier}"
        os.makedirs(card_dir, exist_ok=True)

        image_path = CardManager._to_path(card_dir, IMG_PATH)
        card.image.image.save(image_path)

        metadata = self._get_metadata(card, image_path)
        metadata_path = CardManager._to_path(card_dir, META_PATH)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def load(self, name: str, creator: str) -> Card:
        """load a card by its name and creator"""
        if creator not in self.cards or name not in self.cards[creator]:
            raise ValueError(f"Card '{name}' by '{creator}' not found.")
        identifier = self.cards[creator][name]

        card_dir = CardManager._to_path(
            self.storage_dir, f"{CardManager._card_dir_name(name, creator, identifier)}"
        )
        metadata_path = CardManager._to_path(card_dir, META_PATH)
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        card = Card.create_from_path(
            name=metadata["name"],
            creator=metadata["creator"],
            image_path=metadata["image_path"],
            riddle=metadata["riddle"],
            solution=metadata["solution"],
        )
        return card
