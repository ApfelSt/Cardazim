from __future__ import annotations
import pytest
from connection import Connection
from crypt_image import CryptImage
import client
import server
import threading


@pytest.mark.parametrize(
    "server_ip, server_port, card_name, card_creator, card_riddle, card_solution, card_image_path",
    [
        (
            "127.0.0.1",
            5000,
            "Test Card",
            "Tester",
            "Test?",
            "Test!",
            "image.jpg",
        )
    ],
)
def test_client_server_interaction(
    server_ip,
    server_port,
    card_name,
    card_creator,
    card_riddle,
    card_solution,
    card_image_path,
):
    server_thread = threading.Thread(
        target=server.run_server, args=(server_ip, server_port), daemon=True
    )
    server_thread.start()

    args = client.argparse.Namespace(
        server_ip=server_ip,
        server_port=server_port,
        card_name=card_name,
        card_creator=card_creator,
        card_riddle=card_riddle,
        card_solution=card_solution,
        card_image_path=card_image_path,
    )
    result = client.main(args)
    assert result == 0
