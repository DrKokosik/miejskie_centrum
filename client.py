"""Klient Miejskiego Centrum Usług."""

from __future__ import annotations

import pickle
import socket
import struct
import sys
from typing import Generator

from models import Mieszkaniec, Urzednik, Wniosek

HOST = "127.0.0.1"
PORT = 65432

QUERY_CLASSES = ["Mieszkaniec", "Wniosek", "Urzednik", "NieistniejacaKlasa"]

EXPECTED_TYPES: dict[str, type] = {
    "Mieszkaniec": Mieszkaniec,
    "Wniosek": Wniosek,
    "Urzednik": Urzednik,
}


def recv_line(sock: socket.socket) -> str:
    """Odbiera jedną linię tekstu UTF-8 zakończoną znakiem nowej linii.

    Args:
        sock: Gniazdo, z którego odczytujemy dane.

    Returns:
        Odebrana linia bez końcowego '\\n'.

    Raises:
        ConnectionResetError: Gdy serwer zamknął połączenie przed przesłaniem '\\n'.
    """
    data = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionResetError("Serwer zamknął połączenie.")
        if chunk == b"\n":
            break
        data.extend(chunk)
    return data.decode("utf-8")


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Odbiera dokładnie n bajtów z gniazda.

    Args:
        sock: Gniazdo źródłowe.
        n: Liczba bajtów do odebrania.

    Returns:
        Odebrane bajty (dokładnie n).

    Raises:
        ConnectionResetError: Gdy połączenie zostanie zamknięte przed odebraniem n bajtów.
    """
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionResetError("Połączenie zerwane podczas odbioru danych.")
        data.extend(chunk)
    return bytes(data)


def recv_payload(sock: socket.socket) -> list:
    """Odbiera binarny payload poprzedzony 4-bajtowym prefiksem długości.

    Args:
        sock: Gniazdo źródłowe.

    Returns:
        Zdeserializowana lista obiektów.

    Raises:
        ConnectionResetError: Gdy połączenie zostanie zerwane.
        pickle.UnpicklingError: Gdy dane są niepoprawne.
    """
    length_bytes = recv_exact(sock, 4)
    (length,) = struct.unpack(">I", length_bytes)
    raw = recv_exact(sock, length)
    return pickle.loads(raw)


def check_and_print_objects(
    client_id: str, class_name: str, received_list: list
) -> None:
    """Wypisuje odebrane obiekty i sprawdza zgodność typów.

    Dla każdego obiektu drukuje jego reprezentację tekstową. Jeśli typ obiektu
    nie odpowiada oczekiwanemu typowi dla podanej klasy, drukuje komunikat
    ClassCastException.

    Args:
        client_id: Identyfikator klienta używany w prefiksie logów.
        class_name: Nazwa klasy, której dotyczyło zapytanie.
        received_list: Lista obiektów odebranych z serwera.
    """
    results: Generator[str, None, None] = (str(obj) for obj in received_list)
    for line in results:
        print(f"[CLIENT {client_id}] {line}")

    expected_type = EXPECTED_TYPES.get(class_name)
    for obj in received_list:
        if expected_type is None or not isinstance(obj, expected_type):
            print(
                f"[CLIENT {client_id}] ERROR - ClassCastException: "
                f"expected {class_name}, got {type(obj).__name__}"
            )


def run_client(client_id: str) -> None:
    """Nawiązuje połączenie z serwerem MCU i wykonuje sekwencję zapytań.

    Wysyła identyfikator klienta, odbiera status połączenia, a następnie
    kolejno odpytuje serwer o każdą klasę z QUERY_CLASSES.

    Args:
        client_id: Identyfikator klienta przekazywany serwerowi.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(f"{client_id}\n".encode("utf-8"))

        status = recv_line(sock)
        if status == "REFUSED":
            print(f"[CLIENT {client_id}] Połączenie odrzucone.")
            return

        for class_name in QUERY_CLASSES:
            sock.sendall(f"{class_name}\n".encode("utf-8"))
            received_list = recv_payload(sock)
            check_and_print_objects(client_id, class_name, received_list)

        sock.sendall("QUIT\n".encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python client.py <client_id>")
        sys.exit(1)

    cid = sys.argv[1]
    try:
        run_client(cid)
    except OSError as exc:
        print(f"[CLIENT {cid}] Błąd sieci: {exc}")
    except pickle.UnpicklingError as exc:
        print(f"[CLIENT {cid}] Błąd deserializacji: {exc}")
    except TypeError as exc:
        print(f"[CLIENT {cid}] Błąd typu: {exc}")
    except ConnectionResetError as exc:
        print(f"[CLIENT {cid}] Połączenie zresetowane: {exc}")
