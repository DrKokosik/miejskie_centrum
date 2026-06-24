"""Magazyn danych obiektów MCU."""

from __future__ import annotations

from typing import Any

from models import Mieszkaniec, Urzednik, Wniosek


def build_object_map() -> dict[str, Any]:
    """Tworzy mapę 12 obiektów MCU (4 egzemplarze każdej klasy).

    Returns:
        Słownik z kluczami w formacie '<klasa>_<numer>' (1–4) mapującymi
        na instancje Mieszkaniec, Wniosek i Urzednik.
    """
    return {
        "mieszkaniec_1": Mieszkaniec(
            imie="Anna",
            nazwisko="Kowalska",
            pesel="85030312345",
            adres="ul. Kwiatowa 5/10, 00-001 Warszawa",
        ),
        "mieszkaniec_2": Mieszkaniec(
            imie="Piotr",
            nazwisko="Wiśniewski",
            pesel="72051598765",
            adres="ul. Lipowa 22, 30-001 Kraków",
        ),
        "mieszkaniec_3": Mieszkaniec(
            imie="Maria",
            nazwisko="Nowak",
            pesel="90101054321",
            adres="ul. Różana 8/3, 50-001 Wrocław",
        ),
        "mieszkaniec_4": Mieszkaniec(
            imie="Tomasz",
            nazwisko="Zieliński",
            pesel="65072011223",
            adres="ul. Sosnowa 15, 80-001 Gdańsk",
        ),
        "wniosek_1": Wniosek(
            numer="WN/2024/001",
            typ="dowód osobisty",
            data_zlozenia="2024-01-15",
            status="oczekuje",
        ),
        "wniosek_2": Wniosek(
            numer="WN/2024/002",
            typ="meldunek",
            data_zlozenia="2024-02-20",
            status="w trakcie",
        ),
        "wniosek_3": Wniosek(
            numer="WN/2024/003",
            typ="pozwolenie na budowę",
            data_zlozenia="2024-03-10",
            status="zatwierdzony",
        ),
        "wniosek_4": Wniosek(
            numer="WN/2024/004",
            typ="zasiłek rodzinny",
            data_zlozenia="2024-04-05",
            status="odrzucony",
        ),
        "urzednik_1": Urzednik(
            imie="Katarzyna",
            nazwisko="Wróbel",
            wydzial="Wydział Komunikacji",
            numer_pokoju="101",
        ),
        "urzednik_2": Urzednik(
            imie="Marek",
            nazwisko="Jabłoński",
            wydzial="Wydział Ewidencji Ludności",
            numer_pokoju="205",
        ),
        "urzednik_3": Urzednik(
            imie="Joanna",
            nazwisko="Krawczyk",
            wydzial="Wydział Budownictwa",
            numer_pokoju="312",
        ),
        "urzednik_4": Urzednik(
            imie="Robert",
            nazwisko="Pawlak",
            wydzial="Wydział Spraw Społecznych",
            numer_pokoju="418",
        ),
    }


def get_objects_by_class(obj_map: dict[str, Any], class_name: str) -> list[Any]:
    """Zwraca listę obiektów odpowiadających podanej nazwie klasy.

    Filtruje klucze słownika według prefiksu '<class_name.lower()>_'.

    Args:
        obj_map: Mapa obiektów zwrócona przez build_object_map().
        class_name: Nazwa klasy (np. 'Mieszkaniec' lub 'mieszkaniec').

    Returns:
        Lista pasujących obiektów lub pusta lista, gdy nic nie znaleziono.
    """
    prefix = class_name.lower() + "_"
    return [value for key, value in obj_map.items() if key.startswith(prefix)]
