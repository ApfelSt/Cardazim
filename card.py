from __future__ import annotations
from os import PathLike, stat
from typing import Union
from crypt_image import CryptImage
from PIL import Image

UINT_SIZE = 4  # size of unsigned ints for length prefixes
BYTES_PER_PIXEL = 3  # assuming RGB images
BYTE_ORDER = "little"
PIXEL_FORMAT = "RGB"
HASH_SIZE = 32  # size of SHA-256 hash
DUMMY_KEY = b"\x00" * HASH_SIZE  # placeholder for missing key hash


class Card:
    def __init__(
        self,
        name: str,
        creator: str,
        image: CryptImage,
        riddle: str,
        solution: str | None = None,
    ) -> None:
        self.name = name
        self.creator = creator
        self.image = image
        self.riddle = riddle
        self.solution = solution

    def __repr__(self) -> str:
        return f"<Card name={self.name}, creator={self.creator}>"

    def __str__(self) -> str:
        without_sol = f"Card {self.name} by {self.creator}\nRiddle: {self.riddle}"
        if self.solution:
            return without_sol + f"\nSolution: {self.solution}"
        return without_sol

    @classmethod
    def create_from_path(
        cls,
        name: str,
        creator: str,
        image_path: Union[str, PathLike],
        riddle: str,
        solution: str,
    ) -> Card:
        """create Card instance from image file path"""
        image = CryptImage.create_from_path(image_path)
        return cls(name, creator, image, riddle, solution)

    @staticmethod
    def _int_to_bytes(value: int) -> bytes:
        """convert an integer to bytes of size UINT_SIZE"""
        return value.to_bytes(UINT_SIZE, byteorder=BYTE_ORDER)

    @staticmethod
    def _bytes_to_int(value: bytes) -> int:
        """convert bytes of size UINT_SIZE to an integer"""
        return int.from_bytes(value, byteorder=BYTE_ORDER)

    @staticmethod
    def _serialize_string(data: str) -> bytes:
        """serialize a string to bytes with its length prefixed as 4 bytes"""
        encoded = data.encode()
        length = Card._int_to_bytes(len(encoded))
        return length + encoded

    @staticmethod
    def _serialize_image(image: CryptImage) -> bytes:
        """serialize the image to bytes with its size prefixed"""
        img_bytes = image.image.tobytes()
        height = Card._int_to_bytes(image.image.height)
        width = Card._int_to_bytes(image.image.width)
        return height + width + img_bytes

    def serialize(self) -> bytes:
        """serialize the card to bytes
        format: name_length(4 bytes) | name | creator_length(4 bytes) | creator |
                | image_height(4 bytes) | image_width(4 bytes) | image_data
                | key_hash(4 bytes) | riddle_length(4 bytes) | riddle |
        """
        data = b""
        data += self._serialize_string(self.name)
        data += self._serialize_string(self.creator)
        data += self._serialize_image(self.image)
        if self.image.key_hash:
            data += self.image.key_hash
        else:
            data += DUMMY_KEY
        data += self._serialize_string(self.riddle)
        return data

    @staticmethod
    def _deserialize_string(data: bytes, offset: int) -> tuple[str, int]:
        """deserialize a string from bytes with its length prefixed as 4 bytes"""
        length = Card._bytes_to_int(data[offset : offset + UINT_SIZE])
        offset += UINT_SIZE
        value = data[offset : offset + length].decode()
        offset += length
        return value, offset

    @staticmethod
    def _deserialize_image(data: bytes, offset: int) -> tuple[CryptImage, int]:
        """deserialize the image from bytes with its size prefixed"""
        height = Card._bytes_to_int(data[offset : offset + UINT_SIZE])
        offset += UINT_SIZE
        width = Card._bytes_to_int(data[offset : offset + UINT_SIZE])
        offset += UINT_SIZE
        img_size = height * width * BYTES_PER_PIXEL
        img_data = data[offset : offset + img_size]
        offset += img_size
        image = Image.frombytes(PIXEL_FORMAT, (width, height), img_data)
        key_hash = data[offset : offset + HASH_SIZE]
        offset += HASH_SIZE
        if key_hash != DUMMY_KEY:
            crypt_image = CryptImage(image, key_hash)
        else:
            crypt_image = CryptImage(image, None)
        return crypt_image, offset

    @classmethod
    def deserialize(cls, data: bytes) -> Card:
        """deserialize the card from bytes"""
        offset = 0
        name, offset = cls._deserialize_string(data, offset)
        creator, offset = cls._deserialize_string(data, offset)
        image, offset = cls._deserialize_image(data, offset)
        riddle, offset = cls._deserialize_string(data, offset)
        return cls(name, creator, image, riddle)


"""
The example from the file. this works (delete later).
if __name__ == "__main__":
    name = "Sample Card"
    creator = "Test Creator"
    riddle = "a"
    solution = "A piano"
    path = "image.jpg"
    card = Card.create_from_path(name, creator, path, riddle, solution)
    card.image.encrypt(card.solution)
    data = card.serialize()
    card2 = Card.deserialize(data)
    if card2.image.decrypt(solution):
        card2.solution = solution
    assert repr(card) == repr(card2)
    card2.image.image.show()
"""
