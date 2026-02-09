from __future__ import annotations
from re import M
import sqlite3

from PIL.Image import ID
from uaclient.util import create_package_list_str
from card import Card
from os import PathLike
from typing import Generator, Union
from card_driver import CardDriver
import json
import os

DB_FILE = "cards.db"
IMG_TYPE = "png"
META_TABLE = "metadata"
ID_TABLE = "identifiers"


class SQLDriver(CardDriver):
    def __init__(self, db_path: Union[str, PathLike] = DB_FILE) -> None:
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """create the following tables, dropping existing ones if they exist:
        - metadata: stores card metadata with columns:
            - identifier (TEXT PRIMARY KEY)
            - metadata (TEXT)
        - identifiers: stores card identifiers with columns:
            - creator (TEXT)
            - name (TEXT)
            - identifier (TEXT PRIMARY KEY)
        """
        connection = sqlite3.connect(self.db_path)
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {META_TABLE} (
                identifier TEXT PRIMARY KEY,
                metadata TEXT,
                is_solved INTEGER DEFAULT 0
            )
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {ID_TABLE} (
                creator TEXT,
                name TEXT,
                identifier TEXT PRIMARY KEY
            )
            """
        )
        connection.commit()

    def get_identifier(self, name: str, creator: str) -> str | None:
        """get the unique identifier for the given card.
        If the card does not exist, return None."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.execute(
            f"""
            SELECT identifier FROM {ID_TABLE}
            WHERE creator = ? AND name = ?
        """,
            (creator, name),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_creators(self) -> list[str]:
        """Return a list of card names created by the specified creator."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.execute(
            f"""
            SELECT creator FROM {ID_TABLE}
                                         """
        )
        rows = cursor.fetchall()
        creators = {row[0] for row in rows}
        return list(creators)

    def get_creator_card_names(self, creator: str) -> list[str]:
        """Return a list of card names created by the specified creator."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.execute(
            f"""
            SELECT name FROM {ID_TABLE}
            WHERE creator = ?
                                         """,
            (creator,),
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def load(self, identifier: str) -> dict[str, str] | None:
        """Load the card data associated with the identifier."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.execute(
            f"""
                SELECT metadata from {META_TABLE}
                WHERE identifier = ?
                """,
            (identifier,),
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def get_creator_cards(self, creator: str) -> list[dict[str, str] | None]:
        """Return a list of cards created by the specified creator."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.execute(
            f"""
                SELECT identifier from {ID_TABLE}
                WHERE creator = ?
                """,
            (creator,),
        )
        id_rows = cursor.fetchall()
        identifiers = [row[0] for row in id_rows]
        return [self.load(identifier) for identifier in identifiers]

    def save(self, metadata: dict[str, str], identifier: str) -> None:
        """Save the card data associated with the identifier."""
        is_solved = metadata["solution"] is not None
        connection = sqlite3.connect(self.db_path)
        connection.execute(
            f"""
                INSERT OR REPLACE INTO {META_TABLE} VALUES (?, ?, ?)
                """,
            (identifier, json.dumps(metadata), int(is_solved)),
        )

        connection.execute(
            f"""
                INSERT OR REPLACE INTO {ID_TABLE} VALUES (?, ?, ?)
                """,
            (metadata["creator"], metadata["name"], identifier),
        )

        connection.commit()
