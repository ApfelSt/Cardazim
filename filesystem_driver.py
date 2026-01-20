from __future__ import annotations
from card import Card
from os import PathLike
from typing import Generator, Union
import json
import pathlib
import os
from card_driver import CardDriver
import re

IMG_PATH = "image.jpg"
META_PATH = "metadata.json"
SOLVED_DIR = "solved"
UNSOLVED_DIR = "unsolved"


class FilesystemDriver(CardDriver):
    @staticmethod
    def _to_path(*args: Union[str, PathLike]) -> str:
        """create a file path by joining given parts"""
        return os.path.join(*map(str, args))

    def __init__(self, storage_dir: Union[str, PathLike] = ".") -> None:
        """self.cards: card creator -> card name -> card id"""
        self.storage_dir = pathlib.Path(storage_dir)
        self._create_directory_structure()
        self.cards: dict[str, dict[str, str]] = {}

    def _create_directory_structure(self) -> None:
        """create the directory structure for storing cards:
        storage_dir/
            solved/
            unsolved/
        """
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        solved_dir_path = FilesystemDriver._to_path(self.storage_dir, SOLVED_DIR)
        unsolved_dir_path = FilesystemDriver._to_path(self.storage_dir, UNSOLVED_DIR)
        os.makedirs(solved_dir_path, exist_ok=True)
        os.makedirs(unsolved_dir_path, exist_ok=True)

    def get_identifier(self, name: str, creator: str) -> str | None:
        """get the unique identifier for the given card.
        If the card does not exist, return None."""
        if creator in self.cards and name in self.cards[creator]:
            return self.cards[creator][name]

    def _update_index(self, metadata: dict[str, str], identifier: str) -> None:
        """update the internal index of cards with the given metadata and identifier"""
        creator = metadata["creator"]
        name = metadata["name"]
        if creator not in self.cards:
            self.cards[creator] = {}
        self.cards[creator][name] = identifier

    def save(self, metadata: dict[str, str], identifier: str) -> None:
        """save the given card to the storage directory"""
        status_dir = SOLVED_DIR if metadata["solution"] else UNSOLVED_DIR
        card_dir = FilesystemDriver._to_path(self.storage_dir, status_dir, identifier)
        os.makedirs(card_dir, exist_ok=True)

        metadata_path = FilesystemDriver._to_path(card_dir, META_PATH)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

        self._update_index(metadata, identifier)

    def load(self, identifier: str) -> dict[str, str]:
        """load a card by its identifier. find the card in either solved or unsolved directories and then load."""
        print(f"Loading card with identifier: {identifier}")
        pattern = re.compile(rf".*{identifier}$")
        card_dir = ""
        for status_dir in [SOLVED_DIR, UNSOLVED_DIR]:
            for entry in os.listdir(
                FilesystemDriver._to_path(self.storage_dir, status_dir)
            ):
                if pattern.match(entry):
                    card_dir = FilesystemDriver._to_path(
                        self.storage_dir, status_dir, entry
                    )
                    break
            if card_dir:
                break

        metadata_path = FilesystemDriver._to_path(self.storage_dir, card_dir, META_PATH)
        print(f"Loading metadata from: {metadata_path}")
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return metadata

    def get_creators(self) -> list[str]:
        """get a list of all card creators in the storage"""
        return list(self.cards.keys())

    def get_creator_cards(self, creator: str) -> list[dict[str, str]]:
        """get a list of all card names for the given creator"""
        if creator not in self.cards:
            return []
        return [self.load(card_id) for card_id in self.cards[creator].values()]

    def get_creator_card_names(self, creator: str) -> list[str]:
        """get a list of all card names for the given creator"""
        if creator not in self.cards:
            return []
        return list(self.cards[creator].keys())
