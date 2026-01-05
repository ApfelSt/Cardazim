from __future__ import (
    annotations,
)  # So we can use Connection type hints within the class
import socket
import struct
from types import TracebackType
from typing import Type


class Connection:
    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection
        self.src = self.connection.getsockname()
        self.dst = self.connection.getpeername()

    def __repr__(self) -> str:
        return f"Connection from {self.src} to {self.dst}"

    def __enter__(self) -> Connection:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def send(self, msg: str) -> None:
        """Send a message through the connection."""
        data = msg.encode()
        length = struct.pack("<I", len(data))
        self.connection.sendall(length + data)

    def receive(self) -> str:
        """Receive a message from the connection."""
        try:
            packed = self.connection.recv(4)
            unpacked = struct.unpack("<I", packed)[0]
            data = self.connection.recv(unpacked)
            return data.decode()
        except Exception as error:
            raise ConnectionError(f"Failed to receive message: {error}")

    def close(self) -> None:
        """Close the connection."""
        self.connection.close()

    @classmethod
    def connect(cls, ip: str, port: int) -> Connection:
        """Establish a connection to the given IP and port."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((ip, port))
        return cls(sock)
