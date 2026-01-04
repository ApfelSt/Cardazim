import socket
import argparse
import struct
import sys
from uaclient.yaml import parser
import threading
import time


def handle_client(client_socket: socket.socket, client_address: tuple) -> None:
    """
    Handle a client connection, receive data and print it.
    """
    print(f"Connection from {client_address}")

    length_data = client_socket.recv(4)
    message_length = struct.unpack("<I", length_data)[0]
    message_data = client_socket.recv(message_length)
    message = message_data.decode()

    time.sleep(10)
    print(f"Received message: {message}")

    client_socket.close()


def run_server(ip: str, port: int) -> None:
    """
    Run a simple TCP server that listens on the given IP and port.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip, port))

    print(f"Server listening on {ip}:{port}...")

    while True:
        server_socket.listen()
        client_socket, client_address = server_socket.accept()
        new_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address)
        )
        new_thread.start()


def get_args() -> argparse.Namespace:
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
