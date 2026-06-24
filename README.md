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

Do realizacji projektu wykorzystano narzędzie **Cursor** z modelem **Claude Sonnet 4.5**.

**Zakres użycia:**
- Generowanie szkieletu kodu (models.py, server.py, client.py)
- Pisanie testów jednostkowych, integracyjnych i E2E
- Debugowanie wielowątkowości i protokołu binarnego

**Przykładowy prompt użyty do generacji:**
"Napisz kompletny projekt Python — aplikacja klient-serwer symulująca
Miejskie Centrum Usług. MODELE: Mieszkaniec, Wniosek, Urzednik [@dataclass].
SERWER: MAX_CLIENTS=3, threading.Semaphore, pickle + 4-bajtowy prefix binarny.
KLIENT: generator expression, isinstance check, ClassCastException handling.
TESTY: pytest, 3x unit, 3x integration, 3x E2E z fixture."

Wygenerowany kod został przejrzany i zrozumiany przez zespół.
