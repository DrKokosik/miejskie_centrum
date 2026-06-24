"""Serwer Miejskiego Centrum Usług."""

from __future__ import annotations

import logging
import pickle
import random
import socket
import struct
import threading
import time
from typing import Any

from data_store import build_object_map, get_objects_by_class

HOST = "127.0.0.1"
PORT = 65432
MAX_CLIENTS = 3
MIN_DELAY = 0.5
MAX_DELAY = 2.0

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class MCUServer:
    """Wielowątkowy serwer Miejskiego Centrum Usług.

    Obsługuje do MAX_CLIENTS równoległych połączeń przy użyciu semafora.
    Nadwyżkowe połączenia są natychmiast odrzucane komunikatem REFUSED.
    """

    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        """Inicjalizuje serwer z podanym adresem i portem.

        Args:
            host: Adres IP do nasłuchiwania.
            port: Port TCP (0 = przydzielony przez system).
        """
        self.host = host
        self.port = port
        self.semaphore = threading.Semaphore(MAX_CLIENTS)
        self.lock = threading.Lock()
        self.clients_served: int = 0
        self.requests_handled: int = 0
        self.obj_map: dict[str, Any] = build_object_map()
        self._server_socket: socket.socket | None = None
        self._stop_event = threading.Event()

    def handle_client(
        self, conn: socket.socket, addr: tuple[str, int], client_id: int
    ) -> None:
        """Obsługuje pojedyncze połączenie klienta w osobnym wątku.

        Protokół: serwer wysyła OK/REFUSED, następnie odbiera nazwy klas
        i odsyła listy obiektów zakodowane pickle z 4-bajtowym prefiksem
        długości (big-endian). Pętla kończy się po odebraniu 'QUIT'.

        Args:
            conn: Gniazdo połączonego klienta.
            addr: Adres klienta (host, port).
            client_id: Wewnętrzny identyfikator nadany przez serwer.
        """
        acquired = self.semaphore.acquire(blocking=False)
        if not acquired:
            conn.sendall("REFUSED\n".encode("utf-8"))
            conn.close()
            return

        conn.sendall("OK\n".encode("utf-8"))

        try:
            client_label = self._recv_line(conn)
            logging.info(
                f"Przyjęto klienta {client_label!r} "
                f"(addr={addr}, id={client_id})"
            )

            with self.lock:
                self.clients_served += 1

            while True:
                class_name = self._recv_line(conn)
                if class_name == "QUIT":
                    break

                objects = get_objects_by_class(self.obj_map, class_name)
                if not objects:
                    objects = self._build_decoy_payload()

                payload = pickle.dumps(objects)
                conn.sendall(struct.pack(">I", len(payload)) + payload)

                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                with self.lock:
                    self.requests_handled += 1

                logging.info(
                    f"Wysłano {len(objects)} obiektów klasy {class_name!r} "
                    f"do klienta {client_id}"
                )

        except (OSError, EOFError) as exc:
            logging.warning(f"Klient {client_id} rozłączył się: {exc}")
        finally:
            self.semaphore.release()
            conn.close()
            logging.info(f"Klient {client_id} rozłączony, semaforo zwolniony.")

    def _recv_line(self, conn: socket.socket) -> str:
        """Odbiera jedną linię tekstu UTF-8 zakończoną znakiem nowej linii.

        Args:
            conn: Gniazdo, z którego odczytujemy dane.

        Returns:
            Odebrana linia bez końcowego znaku '\\n'.

        Raises:
            EOFError: Gdy połączenie zostanie zamknięte przed odebraniem '\\n'.
        """
        data = bytearray()
        while True:
            chunk = conn.recv(1)
            if not chunk:
                raise EOFError("Połączenie zamknięte przez klienta.")
            if chunk == b"\n":
                break
            data.extend(chunk)
        return data.decode("utf-8")

    def _build_decoy_payload(self) -> list[Any]:
        """Buduje losowy obiekt zastępczy dla nieznanej klasy.

        Returns:
            Lista zawierająca jeden losowo wybrany obiekt z magazynu danych.
        """
        return [random.choice(list(self.obj_map.values()))]

    def run(self) -> None:
        """Uruchamia serwer i blokuje wątek do momentu przerwania.

        Przy KeyboardInterrupt drukuje statystyki i kończy pracę.
        """
        client_counter = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            self._server_socket = server_socket
            actual_port = server_socket.getsockname()[1]
            logging.info(f"Serwer MCU nasłuchuje na {self.host}:{actual_port}")

            try:
                while True:
                    conn, addr = server_socket.accept()
                    client_counter += 1
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr, client_counter),
                        daemon=True,
                    )
                    thread.start()
            except KeyboardInterrupt:
                logging.info("Zatrzymywanie serwera…")
                self._print_statistics()

    def start_in_background(self) -> int:
        """Uruchamia serwer w wątku demona i zwraca przydzielony port.

        Metoda blokuje, dopóki gniazdo serwera nie jest gotowe do przyjmowania
        połączeń. Serwer można zatrzymać metodą stop().

        Returns:
            Numer portu TCP, na którym nasłuchuje serwer.
        """
        port_ready = threading.Event()
        port_holder: list[int] = []

        def _accept_loop() -> None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv.bind((self.host, self.port))
                srv.listen()
                srv.settimeout(0.1)
                self._server_socket = srv
                port_holder.append(srv.getsockname()[1])
                port_ready.set()

                client_counter = 0
                while not self._stop_event.is_set():
                    try:
                        conn, addr = srv.accept()
                    except socket.timeout:
                        continue
                    except OSError:
                        break
                    client_counter += 1
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr, client_counter),
                        daemon=True,
                    )
                    thread.start()

        server_thread = threading.Thread(target=_accept_loop, daemon=True)
        server_thread.start()
        port_ready.wait(timeout=5.0)
        return port_holder[0]

    def stop(self) -> None:
        """Zatrzymuje serwer i zwalnia zasoby gniazda."""
        self._stop_event.set()
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass

    def _print_statistics(self) -> None:
        """Wypisuje podsumowanie statystyk obsługi klientów."""
        print(f"Obsłużono klientów: {self.clients_served}")
        print(f"Obsłużono zapytań:  {self.requests_handled}")


if __name__ == "__main__":
    server = MCUServer()
    server.run()
