import argparse
import sys
from uaclient.yaml import parser
import threading
from listener import Listener
from connection import Connection


def handle_client(client_connection: Connection) -> None:
    """
    Handle a client connection, receive data and print it.
    """
    with client_connection:
        print(f"Connection from {client_connection.src}")
        data = client_connection.receive()
        if data:
            print(f"Received data: {data}")


def run_server(ip: str, port: int) -> None:
    """
    Run a simple TCP server that listens on the given IP and port.
    """

    with Listener(ip, port) as server_listener:
        print(f"Server listening on {ip}:{port}...")
        while True:
            client_connection = server_listener.accept()
            new_thread = threading.Thread(
                target=handle_client, args=(client_connection,)
            )
            new_thread.start()


def get_args():
    parser = argparse.ArgumentParser(description="Run a server.")
    parser.add_argument("ip", type=str, help="the server IP address")
    parser.add_argument("port", type=int, help="the server port")
    return parser.parse_args()


def main():
    """
    Implementation of CLI and running the server.
    """
    args = get_args()
    try:
        run_server(args.ip, args.port)
    except Exception as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
