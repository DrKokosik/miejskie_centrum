# Miejskie Centrum Usług (MCU)

## Skład zespołu

| Imię         | Rola                        |
|--------------|-----------------------------|
| _Placeholder_ | Programista backendu        |
| _Placeholder_ | Programista backendu        |
| _Placeholder_ | Tester / QA                 |
| _Placeholder_ | Architekt systemu           |

## Opis projektu

Miejskie Centrum Usług (MCU) to symulator wielowątkowego systemu klient-serwer
inspirowanego rzeczywistymi urzędami miejskimi. Serwer przyjmuje do trzech
jednoczesnych połączeń klientów, odsyłając im listy obiektów (mieszkańców,
wniosków i urzędników) zakodowane protokołem binarnym z prefiksem długości.
Klienci odpytują serwer sekwencyjnie o kolejne klasy, wykrywając niezgodności
typów i sygnalizując je komunikatem ClassCastException. Projekt demonstruje
synchronizację wątków za pomocą semafora oraz bezpieczną serializację danych
z użyciem modułu `pickle`.

## Instrukcja uruchomienia

### Instalacja zależności

```bash
pip install -r requirements.txt
```

### Uruchomienie serwera

```bash
python server.py
```

### Uruchomienie klienta

```bash
python client.py 1
```

> Argument `1` to identyfikator klienta — można uruchomić kilka klientów
> w oddzielnych terminalach (np. `python client.py 2`, `python client.py 3`).

### Uruchomienie testów

```bash
pytest tests/ -v
```

## Deklaracja użycia AI

Do wygenerowania szkieletu projektu, testów jednostkowych/integracyjnych/e2e
oraz debugowania mechanizmów wielowątkowości (semafory, wątki demona, poprawne
zamykanie gniazd) wykorzystano **Cursor (Claude Sonnet 4.6)**. Cały wygenerowany
kod został przejrzany i zaakceptowany przez zespół przed włączeniem do repozytorium.
