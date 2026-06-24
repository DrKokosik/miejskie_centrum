"""Testy integracyjne serializacji i protokołu komunikacyjnego MCU."""

from __future__ import annotations

import pickle
import struct

from models import Mieszkaniec, Urzednik, Wniosek


def test_pickle_roundtrip() -> None:
    """Serializacja i deserializacja pickle zachowuje równość obiektów."""
    mieszkaniec = Mieszkaniec(
        "Anna", "Kowalska", "85030312345", "ul. Kwiatowa 5/10, 00-001 Warszawa"
    )
    wniosek = Wniosek("WN/2024/001", "dowód osobisty", "2024-01-15", "oczekuje")
    urzednik = Urzednik("Katarzyna", "Wróbel", "Wydział Komunikacji", "101")

    assert pickle.loads(pickle.dumps(mieszkaniec)) == mieszkaniec
    assert pickle.loads(pickle.dumps(wniosek)) == wniosek
    assert pickle.loads(pickle.dumps(urzednik)) == urzednik


def test_length_prefix_framing() -> None:
    """Prefiks długości 42 pakowany big-endian daje cztery oczekiwane bajty."""
    assert struct.pack(">I", 42) == b"\x00\x00\x00\x2a"


def test_str_contains_all_fields() -> None:
    """Metoda __str__ każdej klasy zawiera wartości wszystkich pól."""
    mieszkaniec = Mieszkaniec(
        "Anna", "Kowalska", "85030312345", "ul. Kwiatowa 5"
    )
    wniosek = Wniosek("WN/2024/001", "dowód osobisty", "2024-01-15", "oczekuje")
    urzednik = Urzednik("Katarzyna", "Wróbel", "Wydział Komunikacji", "101")

    mieszkaniec_str = str(mieszkaniec)
    assert "Anna" in mieszkaniec_str
    assert "Kowalska" in mieszkaniec_str
    assert "85030312345" in mieszkaniec_str
    assert "ul. Kwiatowa 5" in mieszkaniec_str

    wniosek_str = str(wniosek)
    assert "WN/2024/001" in wniosek_str
    assert "dowód osobisty" in wniosek_str
    assert "2024-01-15" in wniosek_str
    assert "oczekuje" in wniosek_str

    urzednik_str = str(urzednik)
    assert "Katarzyna" in urzednik_str
    assert "Wróbel" in urzednik_str
    assert "Wydział Komunikacji" in urzednik_str
    assert "101" in urzednik_str
