import argparse
import sys
from uaclient.yaml import parser
import threading
from listener import Listener
from connection import Connection
from card import Card
from saver import Saver
from typing import Union
from os import PathLike
from card_driver import CardDriver
from filesystem_driver import FilesystemDriver
from sql_driver import SQLDriver


def handle_client(client_connection: Connection, card_manager: Saver) -> None:
    """
    Handle a client connection, receive data and print it.
    """
    with client_connection:
        print(f"Connection from {client_connection.src}")
        data = client_connection.receive()
        if data:
            card = Card.deserialize(data)
            card_manager.save(card)
            print(f"Card saved: {card.name} by {card.creator}")
            loaded_card = card_manager.load(card.name, card.creator)
            print(f"Card loaded: {loaded_card.name} by {loaded_card.creator}")


def run_server(
    ip: str, port: int, driver: CardDriver, dir: Union[str, PathLike] = "images"
) -> None:
    """
    Run a simple TCP server that listens on the given IP and port.
    """
    card_manager = Saver(driver, dir)

    with Listener(ip, port) as server_listener:
        print(f"Server listening on {ip}:{port}...")
        while True:
            client_connection = server_listener.accept()
            new_thread = threading.Thread(
                target=handle_client, args=(client_connection, card_manager)
            )
            new_thread.start()


def get_args():
    parser = argparse.ArgumentParser(description="Run a server.")
    parser.add_argument("ip", type=str, help="the server IP address")
    parser.add_argument("port", type=int, help="the server port")
    parser.add_argument(
        "driver",
        type=str,
        choices=["filesystem", "sql"],
        help="the storage driver to use",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="images",
        help="the directory to store images (for filesystem driver)",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> int | None:
    """
    Implementation of CLI and running the server.
    """
    try:
        match args.driver:
            case "filesystem":
                driver = FilesystemDriver()
            case "sql":
                driver = SQLDriver()
            case _:
                raise ValueError(f"Unknown driver: {args.driver}")
        run_server(args.ip, args.port, driver, args.dir)
    except Exception as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    args = get_args()
    sys.exit(main(args))
