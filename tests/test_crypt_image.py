from __future__ import annotations
from crypt_image import CryptImage
from PIL import Image
import os
import pytest
from os import PathLike
from typing import Union


@pytest.mark.parametrize(
    "image_path, key, tmp_path",
    [
        ("image.jpg", "testkey", "test_path.jpg"),
    ],
)
def test_encrypt_decrypt(
    image_path: Union[str, PathLike], key: str, tmp_path: PathLike
) -> None:
    """test that encrypting and decrypting an image works correctly"""
    crypt_img = CryptImage.create_from_path(image_path)
    crypt_img.encrypt(key)
    crypt_img.decrypt(key)
    crypt_img.image.save(tmp_path)
