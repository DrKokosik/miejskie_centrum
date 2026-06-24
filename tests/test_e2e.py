"""Testy end-to-end serwera MCU z rzeczywistymi połączeniami TCP."""

from __future__ import annotations

import pickle
import socket
import struct

import pytest

from models import Mieszkaniec, Urzednik, Wniosek
from server import MAX_CLIENTS, MCUServer

_HOST = "127.0.0.1"

_EXPECTED_TYPES: dict[str, type] = {
    "Mieszkaniec": Mieszkaniec,
    "Wniosek": Wniosek,
    "Urzednik": Urzednik,
}


@pytest.fixture
def server_port() -> pytest.FixtureYield[int]:
    """Uruchamia serwer MCU na losowym porcie i zwraca jego numer.

    Yields:
        Numer portu TCP przydzielony przez system operacyjny.
    """
    srv = MCUServer(_HOST, 0)
    port = srv.start_in_background()
    yield port
    srv.stop()


def _send_line(sock: socket.socket, text: str) -> None:
    """Wysyła tekst zakończony znakiem nowej linii przez gniazdo."""
    sock.sendall((text + "\n").encode("utf-8"))


def _recv_line(sock: socket.socket) -> str:
    """Odbiera jedną linię tekstu zakończoną znakiem nowej linii."""
    data = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk or chunk == b"\n":
            break
        data.extend(chunk)
    return data.decode("utf-8")


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Odbiera dokładnie n bajtów z gniazda."""
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError("Połączenie zamknięte.")
        data.extend(chunk)
    return bytes(data)


def _recv_payload(sock: socket.socket) -> list:
    """Odbiera payload z 4-bajtowym prefiksem długości i deserializuje pickle."""
    length_bytes = _recv_exact(sock, 4)
    (length,) = struct.unpack(">I", length_bytes)
    raw = _recv_exact(sock, length)
    return pickle.loads(raw)


def _connect_and_handshake(port: int, client_id: str) -> tuple[socket.socket, str]:
    """Łączy się z serwerem, wysyła identyfikator i odbiera status.

    Args:
        port: Port serwera.
        client_id: Identyfikator przekazywany serwerowi.

    Returns:
        Krotka (gniazdo, status), gdzie status to 'OK' lub 'REFUSED'.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((_HOST, port))
    _send_line(sock, client_id)
    status = _recv_line(sock)
    return sock, status


def test_clients_within_limit(server_port: int) -> None:
    """Dokładnie MAX_CLIENTS klientów jednocześnie otrzymuje status OK."""
    sockets: list[socket.socket] = []
    try:
        for i in range(MAX_CLIENTS):
            sock, status = _connect_and_handshake(server_port, f"client_{i + 1}")
            assert status == "OK", (
                f"Klient {i + 1} powinien dostać OK, dostał: {status!r}"
            )
            sockets.append(sock)
    finally:
        for sock in sockets:
            try:
                _send_line(sock, "QUIT")
                sock.close()
            except OSError:
                pass


def test_excess_client_refused(server_port: int) -> None:
    """Klient przekraczający limit MAX_CLIENTS otrzymuje status REFUSED."""
    sockets: list[socket.socket] = []
    try:
        for i in range(MAX_CLIENTS):
            sock, status = _connect_and_handshake(server_port, f"client_{i + 1}")
            assert status == "OK"
            sockets.append(sock)

        extra_sock, extra_status = _connect_and_handshake(
            server_port, "extra_client"
        )
        assert extra_status == "REFUSED", (
            f"Czwarty klient powinien dostać REFUSED, dostał: {extra_status!r}"
        )
        extra_sock.close()
    finally:
        for sock in sockets:
            try:
                _send_line(sock, "QUIT")
                sock.close()
            except OSError:
                pass


def test_cast_error_handling(
    server_port: int, capsys: pytest.CaptureFixture[str]
) -> None:
    """Zapytanie o nieznaną klasę wywołuje wydruk ClassCastException."""
    queried_class = "NieistniejacaKlasa"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((_HOST, server_port))
        _send_line(sock, "test_cast_client")
        status = _recv_line(sock)
        assert status == "OK"

        _send_line(sock, queried_class)
        received_list = _recv_payload(sock)

        expected_type = _EXPECTED_TYPES.get(queried_class)
        for obj in received_list:
            if expected_type is None or not isinstance(obj, expected_type):
                print(
                    f"[CLIENT test] ERROR - ClassCastException: "
                    f"expected {queried_class}, got {type(obj).__name__}"
                )

        _send_line(sock, "QUIT")

    captured = capsys.readouterr()
    assert "ClassCastException" in captured.out
