# Todoist API

Aplikacja do zarządzania zadaniami zbudowana przy użyciu FastAPI i SQLite.

[![Codecov](https://codecov.io/gh/usterk/todoist/branch/master/graph/badge.svg)](https://codecov.io/gh/usterk/todoist)

## Struktura projektu

```
todoist/
├── app/                     # Kod źródłowy aplikacji
│   ├── api/                 # Moduł z endpointami API
│   ├── auth/                # Moduł uwierzytelniania
│   ├── core/                # Konfiguracja i funkcje pomocnicze
│   ├── database/            # Obsługa i konfiguracja bazy danych
│   ├── models/              # Modele ORM SQLAlchemy
│   └── schemas/             # Schematy Pydantic do walidacji danych
├── data/                    # Katalog przechowujący bazę danych SQLite
├── docs/                    # Dokumentacja projektu
├── tests/                   # Testy jednostkowe i integracyjne
├── Dockerfile               # Konfiguracja konteneryzacji
├── requirements.txt         # Zależności Python
├── entrypoint.sh            # Skrypt wejściowy dla kontenera
└── run.sh                   # Skrypt do uruchamiania aplikacji w Dockerze
```

## Wymagania

- Python 3.9+
- Docker
- Dostęp do internetu do pobrania zależności

## Uruchomienie aplikacji

### Przy użyciu Dockera

Aplikację można uruchomić przy użyciu skryptu `run.sh`, który automatycznie buduje obraz Docker i uruchamia kontener:

```bash
# Nadaj uprawnienia wykonywania skryptowi (tylko raz)
chmod +x run.sh

# Uruchom aplikację z domyślną nazwą
./run.sh

# Lub podaj własną nazwę aplikacji
./run.sh app moja-aplikacja
```

Skrypt automatycznie:
1. Wykryje zmiany w plikach Dockerfile, requirements.txt lub entrypoint.sh i przebuduje obraz w razie potrzeby
2. Zatrzyma i usunie istniejący kontener z tą samą nazwą
3. Utworzy katalog dla danych, jeśli nie istnieje
4. Uruchomi kontener z odpowiednimi mountami dla kodu i danych

### Uruchamianie testów w kontenerze

Możesz uruchomić testy w kontenerze Docker za pomocą komendy:

```bash
# Uruchom wszystkie testy
./run.sh test

# Uruchom testy z podaną nazwą aplikacji
./run.sh test moja-aplikacja

# Uruchom określone testy lub z dodatkowymi parametrami
./run.sh test moja-aplikacja tests/api/
./run.sh test moja-aplikacja -v tests/api/test_health.py
```

### Dostęp do powłoki w kontenerze

Aby uzyskać dostęp do powłoki bash wewnątrz kontenera:

```bash
./run.sh shell moja-aplikacja
```

### Pomoc

Aby wyświetlić pomoc dotyczącą używania skryptu run.sh:

```bash
./run.sh help
```

### Bez Dockera

Jeśli wolisz uruchomić aplikację bezpośrednio:

```bash
# Utwórz i aktywuj wirtualne środowisko (opcjonalnie)
python -m venv venv
source venv/bin/activate  # W systemie Windows: venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom serwer rozwojowy
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

# Uruchom testy
pytest
```

## Dostęp do API

Po uruchomieniu, API jest dostępne pod adresem:
- http://localhost:5000/

Dokumentacja Swagger UI:
- http://localhost:5000/docs

Dokumentacja ReDoc:
- http://localhost:5000/redoc

## Dostęp do bazy danych

Aplikacja używa SQLite jako bazy danych, z plikiem znajdującym się w katalogu `data/`.
W kontenerze baza danych jest montowana jako wolumin, więc dane są zachowywane pomiędzy uruchomieniami.

## Endpointy API

### Zdrowotność aplikacji

```
GET /health
```

Sprawdza status API i połączenie z bazą danych.

### Autoryzacja

```
POST /api/auth/register
POST /api/auth/login
```

Służą do rejestracji nowego użytkownika i logowania.
