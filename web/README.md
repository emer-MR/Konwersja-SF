# Konwerter SF - Wersja Webowa

Aplikacja webowa do konwersji sprawozdań finansowych XML na Excel.

## Funkcjonalności

- Rejestracja i logowanie użytkowników
- Upload plików XML (e-Sprawozdania)
- Konwersja do XLSX (Bilans + RZiS)
- Limit 10 konwersji dziennie
- Historia konwersji

## Stack technologiczny

- **Backend:** FastAPI + Uvicorn
- **Baza danych:** SQLite (async)
- **Frontend:** Jinja2 + HTMX + Pico CSS
- **Konteneryzacja:** Docker

## Uruchomienie lokalne

### 1. Zainstaluj zależności

```bash
cd web
pip install -r requirements.txt
```

### 2. Uruchom serwer deweloperski

```bash
python run_local.py
```

Lub bezpośrednio:

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Otwórz przeglądarkę

- Aplikacja: http://localhost:8000
- Dokumentacja API: http://localhost:8000/docs

## Uruchomienie na Docker (Synology NAS)

### 1. Przygotuj konfigurację

```bash
cp .env.example .env
# Edytuj .env i ustaw SECRET_KEY
```

### 2. Zbuduj i uruchom

```bash
docker-compose up -d --build
```

### 3. Sprawdź status

```bash
docker-compose logs -f
```

Aplikacja będzie dostępna pod adresem: `http://twoj-nas:8080`

## Struktura projektu

```
web/
├── app/
│   ├── __init__.py
│   ├── main.py           # Główna aplikacja FastAPI
│   ├── config.py         # Konfiguracja
│   ├── database.py       # SQLAlchemy async
│   ├── models.py         # Modele (User, Conversion)
│   ├── schemas.py        # Schematy Pydantic
│   ├── auth.py           # Autoryzacja JWT
│   ├── converter_simple.py  # Uproszczony konwerter
│   ├── api/
│   │   ├── auth_routes.py
│   │   └── convert_routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── convert.html
│   │   └── partials/
│   └── static/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_local.py
└── README.md
```

## Konfiguracja na Synology

### Wymagania

- Docker zainstalowany na NAS
- Dostęp SSH lub File Station

### Instrukcja

1. Skopiuj folder `web/` oraz `src/` na NAS (np. do `/volume1/docker/konwerter-sf/`)

2. Utwórz plik `.env`:
   ```bash
   cd /volume1/docker/konwerter-sf/web
   cp .env.example .env
   nano .env  # ustaw SECRET_KEY
   ```

3. Zbuduj kontener:
   ```bash
   docker-compose up -d --build
   ```

4. (Opcjonalnie) Dodaj do Reverse Proxy w DSM:
   - Panel sterowania → Brama aplikacji → Reverse Proxy
   - Źródło: `https://sf.twoja-domena.pl`
   - Cel: `http://localhost:8080`

## Limity i bezpieczeństwo

- Max 10 konwersji/dzień/użytkownik
- Max rozmiar pliku: 10 MB
- Pliki tymczasowe usuwane po konwersji
- Hasła hashowane bcrypt
- Tokeny JWT (24h ważności)
