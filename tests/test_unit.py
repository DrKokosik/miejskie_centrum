"""Testy jednostkowe modeli i magazynu danych MCU."""

from __future__ import annotations

import re

from data_store import build_object_map, get_objects_by_class
from models import Mieszkaniec


def test_equality_by_key_field() -> None:
    """Równość Mieszkańca wyznaczana jest wyłącznie przez numer PESEL."""
    shared_pesel = "85030312345"
    mieszkaniec_a = Mieszkaniec("Anna", "Kowalska", shared_pesel, "ul. A 1")
    mieszkaniec_b = Mieszkaniec("Anna", "Kowalska", shared_pesel, "ul. B 2")
    mieszkaniec_c = Mieszkaniec("Jan", "Nowak", "99999999999", "ul. C 3")

    assert mieszkaniec_a == mieszkaniec_b
    assert mieszkaniec_a != mieszkaniec_c


def test_build_object_map() -> None:
    """Mapa zawiera dokładnie 12 kluczy, każdy w formacie '<klasa>_<1-4>'."""
    key_pattern = re.compile(r"^[a-z]+_[1-4]$")
    obj_map = build_object_map()

    assert len(obj_map) == 12
    for key in obj_map:
        assert key_pattern.match(key), (
            f"Klucz {key!r} nie pasuje do wzorca r'^[a-z]+_[1-4]$'"
        )


def test_get_objects_by_class() -> None:
    """Filtracja zwraca 4 obiekty dla istniejącej klasy i [] dla nieznanej."""
    obj_map = build_object_map()

    mieszkancy = get_objects_by_class(obj_map, "mieszkaniec")
    assert len(mieszkancy) == 4

    nieznana = get_objects_by_class(obj_map, "nieznana")
    assert nieznana == []
