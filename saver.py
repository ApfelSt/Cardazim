from __future__ import annotations
from card import Card
from os import PathLike
from typing import Generator, Union
import json
import pathlib
import os
from card_driver import CardDriver

IMG_PATH = "image.jpg"
META_PATH = "metadata.json"
SOLVED_DIR = "solved"
UNSOLVED_DIR = "unsolved"
IMG_TYPE = "jpg"


class Saver:
    @staticmethod
    def _generate_identifier() -> Generator[str, None, None]:
        """generate unique identifiers as strings, starting from '0' and incrementing by 1"""
        id = 0
        while True:
            yield str(id)
            id += 1

    @staticmethod
    def _to_identifier(name: str, creator: str, id: str = "") -> str:
        """generate the directory name for a card based on its name and creator"""
        return f"{creator}_{name}_{id}"

    @staticmethod
    def _to_path(*args: Union[str, PathLike]) -> str:
        """create a file path by joining given parts"""
        return os.path.join(*map(str, args))

    def __init__(self, driver: CardDriver, image_dir: Union[str, PathLike]) -> None:
        self.driver = driver
        self.image_dir = pathlib.Path(image_dir)
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self._id_generator = self._generate_identifier()

    def get_identifier(self, card: Card) -> str:
        """get or create a unique identifier for the given card.
        If the card already exists, return its existing identifier."""
        name = card.name
        creator = card.creator

        if (
            creator in self.driver.get_creators()
            and name in self.driver.get_creator_cards(creator)
        ):
            return self.driver.get_identifier(name, creator)

        new_id = next(self._id_generator)
        return Saver._to_identifier(name, creator, new_id)

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
        image_name = f"{identifier}.{IMG_TYPE}"

        image_path = Saver._to_path(self.image_dir, image_name)
        card.image.image.save(image_path)

        metadata = self._get_metadata(card, image_path)
        self.driver.save(metadata, identifier)

    def load(self, name: str, creator: str) -> Card:
        """load a card by its name and creator"""
        if (
            creator not in self.driver.get_creators()
            or name not in self.driver.get_creator_card_names(creator)
        ):
            raise ValueError(f"Creator '{creator}' not found.")

        identifier = self.driver.get_identifier(name, creator)
        metadata = self.driver.load(identifier)

        card = Card.create_from_path(
            name=metadata["name"],
            creator=metadata["creator"],
            image_path=metadata["image_path"],
            riddle=metadata["riddle"],
            solution=metadata["solution"],
        )
        return card
