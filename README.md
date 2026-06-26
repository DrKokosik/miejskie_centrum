# Miejskie Centrum Usług (MCU)

## Skład zespołu

| Imię               | Rola                        |
|--------------------|-----------------------------|
| Jakub Jaczewski    | Programista backendu        |
| Juliusz Kossak     | Architekt systemu           |

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

Do realizacji projektu wykorzystano narzędzie **Cursor** z modelem **Claude Sonnet 4.6**.

**Zakres użycia:**
- Generowanie szkieletu serwera TCP (`server.py`) — obsługa gniazd i pętla akceptacji połączeń
- Debugowanie wielowątkowości i protokołu binarnego
- Pisanie testów jednostkowych

**Przykładowy prompt użyty do generacji:**
> „Napisz klasę MCUServer w Pythonie obsługującą do 3 jednoczesnych połączeń TCP
> przy użyciu `threading.Semaphore`. Dane przesyłaj przez gniazdo jako bajty
> serializowane przez `pickle` z 4-bajtowym nagłówkiem długości (big-endian, `struct.pack('>I', ...)`)."
