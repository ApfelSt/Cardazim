from __future__ import annotations
from card import Card
from os import PathLike
from typing import Generator, Union
import json
import pathlib
import os
from card_driver import CardDriver
from crypt_image import CryptImage

IMG_PATH = "image.png"
META_PATH = "metadata.json"
SOLVED_DIR = "solved"
UNSOLVED_DIR = "unsolved"
IMG_TYPE = "png"


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

        identifier = self.driver.get_identifier(name, creator)
        if identifier:
            return identifier

        new_id = next(self._id_generator)
        return Saver._to_identifier(name, creator, new_id)

    def _to_metadata(
        self, card: Card, image_path: Union[str, PathLike]
    ) -> dict[str, str]:
        """get metadata dictionary for the given card"""
        metadata = {
            "name": card.name,
            "creator": card.creator,
            "riddle": card.riddle,
            "solution": card.solution,
            "image_path": str(image_path),
            "key_hash": (card.image.key_hash.hex() if card.image.key_hash else ""),
        }
        return metadata

    def save(self, card: Card) -> None:
        """save the given card to the storage directory"""
        identifier = self.get_identifier(card)
        image_name = f"{identifier}.{IMG_TYPE}"

        image_path = Saver._to_path(self.image_dir, image_name)
        card.image.image.save(image_path)

        metadata = self._to_metadata(card, image_path)
        self.driver.save(metadata, identifier)

    def _to_card(self, metadata: dict[str, str]) -> Card:
        """convert metadata dictionary to a Card instance"""
        return Card.create_from_path(
            name=metadata["name"],
            creator=metadata["creator"],
            image_path=metadata["image_path"],
            riddle=metadata["riddle"],
            solution=metadata["solution"],
        )

    def _load_metadata(self, name: str, creator: str) -> dict[str, str] | None:
        """load the metadata of the card"""
        identifier = self.driver.get_identifier(name, creator)
        if not identifier:
            return None
        metadata = self.driver.load(identifier)
        return metadata

    def load(self, name: str, creator: str) -> Card | None:
        """load a card by its name and creator"""
        metadata = self._load_metadata(name, creator)

        if not metadata:
            return None

        return self._to_card(metadata)

    def get_creators(self) -> list[str]:
        """get a list of all creators"""
        return self.driver.get_creators()

    def get_creator_cards(
        self, creator: str, solved: bool = False, all: bool = False
    ) -> list[Card]:
        """get a list of cards for a specific creator, filtered by solved status"""
        card_metas = self.driver.get_creator_cards(creator)
        cards: list[Card] = []
        for meta in card_metas:
            if not meta:
                continue
            if all:
                cards.append(self._to_card(meta))
            elif solved == (meta["solution"] is not None):
                cards.append(self._to_card(meta))
        return cards

    def get_creator_card_names(
        self, creator: str, solved: bool = False, all: bool = False
    ) -> list[str]:
        """get a list of card names for a specific creator"""
        return [card.name for card in self.get_creator_cards(creator, solved, all)]

    @staticmethod
    def get_metadata(card: Card) -> dict[str, str]:
        """get metadata dictionary for the given card"""
        metadata = {
            "name": card.name,
            "creator": card.creator,
            "riddle": card.riddle,
            "solution": card.solution,
        }
        return metadata

    def get_image_path(self, name: str, creator: str) -> Union[str, PathLike] | None:
        metadata = self._load_metadata(name, creator)
        return metadata["image_path"] if metadata else None

    def find_cards(self, **query_params: str) -> list[Card]:
        """find all cards that have the query as a substring in their metadata values"""
        matching_cards: list[Card] = []
        creators = self.get_creators()
        for creator in creators:
            cards = self.get_creator_cards(creator, all=True)
            for card in cards:
                match = True
                for key, value in query_params.items():
                    card_value = getattr(card, key, "")
                    if value not in card_value:
                        match = False
                        break
                if match:
                    matching_cards.append(card)
        return matching_cards

    def solve_card(self, name: str, creator: str, solution: str) -> bool:
        """mark the card as solved if the solution is correct"""
        metadata = self._load_metadata(name, creator)
        if not metadata:
            return False
        if not metadata["key_hash"]:
            return False  # no encryption, cannot solve

        key_hash = metadata["key_hash"]
        key_hash = bytes.fromhex(key_hash)
        encrypted_image = CryptImage.create_from_path(metadata["image_path"], key_hash)
        print(
            f"DEBUG: Attempting to solve card '{name}' by '{creator}' with solution '{solution}'"
        )
        sol_check = encrypted_image.decrypt(solution)
        if not sol_check:
            return False

        # update the card metadata to remove the key_hash and add the solution
        os.remove(metadata["image_path"])
        encrypted_image.image.save(metadata["image_path"])

        metadata["solution"] = solution
        metadata["key_hash"] = ""
        identifier = self.driver.get_identifier(name, creator)
        if not identifier:
            return False
        self.driver.save(metadata, identifier)
        return True

    def clear_db(self) -> None:
        """clear the database by removing all metadata and images"""
        self.driver.clear()
        for entry in os.listdir(self.image_dir):
            entry_path = self.image_dir / entry
            if entry_path.is_file():
                os.remove(entry_path)

    def init_db(self) -> None:
        """initialize the database with sample data"""
        self.clear_db()
        # self.init_simple_db()

    def init_simple_db(self) -> None:
        """initialize a simple database by scanning the image directory"""
        card = Card.create_from_path(
            name="Arazim",
            creator="Erez",
            image_path="image.png",
            riddle="What has keys but can't open locks?",
            solution="A piano",
        )
        self.save(card)
        card = Card.create_from_path(
            name="Talpiot",
            creator="Gani",
            image_path="image2.png",
            riddle="Who is the king of nabaz?",
            solution="Gani",
        )
        self.save(card)

        img = CryptImage.create_from_path("image2.png")
        img.encrypt("mooli")
        card = Card(
            name="Secret", creator="Gani", image=img, riddle="Who is the king of nabaz?"
        )
        self.save(card)
        # self.solve_card("Secret", "Gani", "mooli")
