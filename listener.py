from __future__ import annotations
import socket
from connection import Connection
from typing import Type
from types import TracebackType


class Listener:
    def __init__(self, ip: str, port: int, backlog: int = 1000) -> None:
        self.ip = ip
        self.port = port
        self.backlog = backlog
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))

    def __repr__(self) -> str:
        return f"Listener(port={self.port}, host={self.ip}, backlog={self.backlog})"

    def start(self) -> None:
        """Start listening for incoming connections."""
        self.server_socket.listen(self.backlog)

    def stop(self) -> None:
        """Close the listener socket."""
        self.server_socket.close()

    def accept(self) -> Connection:
        """Accept an incoming connection and return a Connection object."""
        client_socket, _ = self.server_socket.accept()
        return Connection(client_socket)

    def __enter__(self) -> Listener:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.stop()
