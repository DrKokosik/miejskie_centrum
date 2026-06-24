"""Modele danych Miejskiego Centrum Usług."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Mieszkaniec:
    """Reprezentuje mieszkańca korzystającego z usług MCU.

    Attributes:
        imie: Imię mieszkańca.
        nazwisko: Nazwisko mieszkańca.
        pesel: Numer PESEL (unikalny identyfikator).
        adres: Adres zamieszkania.
    """

    imie: str
    nazwisko: str
    pesel: str
    adres: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mieszkaniec):
            return NotImplemented
        return self.pesel == other.pesel

    def __hash__(self) -> int:
        return hash(self.pesel)

    def __str__(self) -> str:
        return (
            f"Mieszkaniec[imie={self.imie}, nazwisko={self.nazwisko}, "
            f"pesel={self.pesel}, adres={self.adres}]"
        )


@dataclass
class Wniosek:
    """Reprezentuje wniosek złożony w MCU.

    Attributes:
        numer: Unikalny numer wniosku w formacie WN/RRRR/NNN.
        typ: Rodzaj wniosku (np. 'dowód osobisty').
        data_zlozenia: Data złożenia w formacie RRRR-MM-DD.
        status: Aktualny status wniosku.
    """

    numer: str
    typ: str
    data_zlozenia: str
    status: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Wniosek):
            return NotImplemented
        return self.numer == other.numer

    def __hash__(self) -> int:
        return hash(self.numer)

    def __str__(self) -> str:
        return (
            f"Wniosek[numer={self.numer}, typ={self.typ}, "
            f"data_zlozenia={self.data_zlozenia}, status={self.status}]"
        )


@dataclass
class Urzednik:
    """Reprezentuje urzędnika pracującego w MCU.

    Attributes:
        imie: Imię urzędnika.
        nazwisko: Nazwisko urzędnika.
        wydzial: Nazwa wydziału, w którym pracuje.
        numer_pokoju: Numer pokoju urzędnika.
    """

    imie: str
    nazwisko: str
    wydzial: str
    numer_pokoju: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Urzednik):
            return NotImplemented
        return (
            self.imie == other.imie
            and self.nazwisko == other.nazwisko
            and self.wydzial == other.wydzial
        )

    def __hash__(self) -> int:
        return hash((self.imie, self.nazwisko, self.wydzial))

    def __str__(self) -> str:
        return (
            f"Urzednik[imie={self.imie}, nazwisko={self.nazwisko}, "
            f"wydzial={self.wydzial}, numer_pokoju={self.numer_pokoju}]"
        )
