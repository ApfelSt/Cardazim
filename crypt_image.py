from __future__ import annotations
from PIL import Image
import hashlib
from Crypto.Cipher import AES
from os import PathLike
from Crypto.Cipher._mode_eax import EaxMode
from typing import Union

NUM_ITERS = 2  # Number of iterations for key hashing
NONCE = b"arazim"


class CryptImage:
    def __init__(self, image: Image.Image, key_hash: bytes | None) -> None:
        self.image = image
        self.key_hash = key_hash

    @classmethod
    def create_from_path(
        cls, image_path: Union[str, PathLike], key_hash: bytes | None = None
    ) -> CryptImage:
        """create CryptImage instance from image file path"""
        image = Image.open(image_path)
        return cls(image, key_hash)

    @staticmethod
    def _hash_key(key: str, n: int = NUM_ITERS) -> bytes:
        """use NUM_ITERS iterations of sha256 to hash the key"""
        hashed_key = key.encode()
        for _ in range(n):
            hashed_key = hashlib.sha256(hashed_key).digest()
        return hashed_key

    @staticmethod
    def _create_cipher(key: str) -> EaxMode:
        """create AES cipher with sha256(key)"""
        hashed_key = CryptImage._hash_key(key, 1)
        return AES.new(hashed_key, AES.MODE_EAX, nonce=NONCE)

    def _load_image_from_bytes(self, image: bytes) -> None:
        """load image from bytes"""
        self.image = Image.frombytes(self.image.mode, self.image.size, image)

    def encrypt(self, key: str | None) -> None:
        """encrypt the image with sha256(key)"""
        if key is None:
            raise ValueError("Key must be provided for encryption")
        cipher = CryptImage._create_cipher(key)
        encrypted_image = cipher.encrypt(self.image.tobytes())
        self._load_image_from_bytes(encrypted_image)
        self.key_hash = CryptImage._hash_key(key)

    def decrypt(self, key: str) -> bool:
        """decrypt the image with sha256(key) if the key is correct"""
        if CryptImage._hash_key(key) != self.key_hash:
            return False
        cipher = CryptImage._create_cipher(key)
        decrypted_image = cipher.decrypt(self.image.tobytes())
        self._load_image_from_bytes(decrypted_image)
        self.key_hash = None
        return True
