# Dokumentacja Czytnik SF

## Informacje ogólne

| Parametr | Wartość |
|----------|---------|
| Nazwa | Czytnik SF |
| Wersja | 3.0.0 |
| Framework | FastAPI (Python 3.11) |
| Baza danych | SQLite (async via aiosqlite) — tylko konta admin |
| Frontend | Jinja2 + HTMX (self-contained CSS, bez frameworków) |
| Domena produkcyjna | czytnik.analizy.io |
| Hosting | Hostinger VPS z Traefik + Let's Encrypt |
| Właściciel | Fundacja Modulo (KRS: 0001046866) |

## Funkcjonalność

Aplikacja umożliwia bezpłatną konwersję polskich e-Sprawozdań finansowych z formatu XML na Excel (XLSX) — bez rejestracji.

### Funkcje główne
- Konwersja XML → XLSX (Bilans, RZiS, Nota podatkowa, Zestawienie zmian, Przepływy)
- Obsługa jednostek: Mikro, Małe, Inne (schematy v1-0, v1-2, v1-3)
- Warianty walutowe: PLN i tys. PLN
- Wyodrębnianie załączników PDF z XML
- Disclaimer informacyjny w generowanych plikach XLSX
- Google reCAPTCHA v2 (ochrona antyspamowa)
- Google Analytics z GDPR cookie consent
- Baner bezpieczeństwa (sessionStorage)

### Prywatność
- **Brak gromadzenia danych** o konwersjach (nazw plików, firm, NIP-ów)
- Pliki wejściowe usuwane natychmiast po konwersji
- Pliki wyjściowe dostępne 5 minut, potem automatycznie usuwane
- Cookie consent z opcją "Tylko niezbędne"

### Panel administracyjny
- Logowanie JWT (konto tworzone ręcznie przez CLI)
- Dashboard z listą konwersji (puste gdy ADMIN_FILE_RETENTION_DAYS=0)

## Architektura

```
web/
├── app/
│   ├── main.py              # Główna aplikacja FastAPI, endpointy
│   ├── config.py            # Konfiguracja (Settings z pydantic)
│   ├── models.py            # Modele SQLAlchemy (User, Conversion)
│   ├── database.py          # Połączenie z bazą danych
│   ├── auth.py              # Autentykacja JWT (tylko admin)
│   ├── schemas.py           # Schematy Pydantic
│   ├── xml_validator.py     # Walidacja XML (ochrona XXE)
│   ├── converter_simple.py  # Logika konwersji XML → XLSX
│   ├── templates/
│   │   ├── base.html        # Szablon bazowy (CSS + JS + modale)
│   │   ├── index.html       # Strona główna z konwerterem
│   │   ├── privacy.html     # Redirect → modal w base.html
│   │   ├── terms.html       # Redirect → modal w base.html
│   │   ├── admin/
│   │   │   ├── login.html   # Logowanie admina
│   │   │   └── dashboard.html # Panel admina
│   │   ├── download_expired.html # Strona wygaśnięcia linku
│   │   └── partials/
│   │       └── conversion_result.html # Wynik konwersji (HTMX)
│   └── static/
│       └── favicon.ico      # Teal z białą literą A
├── docker-compose.yml           # Dla Synology NAS
├── docker-compose.hostinger.yml # Dla Hostinger VPS (z Traefik)
├── Dockerfile.prod              # Dockerfile produkcyjny
├── requirements.txt             # Zależności Python
├── create_admin.py              # Skrypt tworzenia admina
├── run_local.py                 # Uruchomienie lokalne
└── .env.example                 # Przykładowa konfiguracja
```

## Frontend

### Wzorzec
Strona wzorowana na kalkulator.analizy.io (PPS Maker). Wspólne elementy:
- Gradient teal header (nie-sticky)
- Baner bezpieczeństwa z disclaimerem
- Fixed footer z linkami: Regulamin | Polityka prywatności | Ustawienia cookies
- Cookie consent (ciemne tło #1e293b)
- Modale dla regulaminu i polityki prywatności (zamiast osobnych stron)
- Self-contained CSS w base.html (bez zewnętrznych frameworków)

### Technologie frontend
- HTMX 1.9.10 (CDN) — dynamiczne wyniki konwersji
- Brak: Pico CSS, themes.css, theme-switcher.js (usunięte w v3.0)

## Endpointy

### Publiczne
| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/` | Strona główna z konwerterem |
| GET | `/polityka-prywatnosci` | Redirect do / (treść w modalu) |
| GET | `/regulamin` | Redirect do / (treść w modalu) |
| POST | `/htmx/convert` | Konwersja pliku (HTMX) |
| GET | `/download/{session_id}` | Pobranie pliku (5 min) lub strona wygaśnięcia |

### Administracyjne
| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/admin/login` | Strona logowania |
| POST | `/admin/login` | Obsługa logowania |
| GET | `/admin/logout` | Wylogowanie |
| GET | `/admin` | Panel z listą konwersji |
| GET | `/admin/download/{id}` | Pobranie pliku z archiwum |

## Konfiguracja (.env)

```env
# WYMAGANE
SECRET_KEY=klucz-32-znaki-hex          # Klucz JWT
RECAPTCHA_SITE_KEY=klucz-publiczny     # reCAPTCHA
RECAPTCHA_SECRET_KEY=klucz-prywatny    # reCAPTCHA

# OPCJONALNE
DEBUG=false                             # Tryb debug
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
MAX_UPLOAD_SIZE_MB=10                   # Max rozmiar pliku
USER_FILE_EXPIRY_MINUTES=5              # Czas życia linku dla użytkownika
ADMIN_FILE_RETENTION_DAYS=0             # 0 = nie gromadź danych o konwersjach
GA_MEASUREMENT_ID=G-BD3959F2HL          # Google Analytics
CONTACT_EMAIL=kontakt@analizy.io        # Email kontaktowy
```

### ADMIN_FILE_RETENTION_DAYS
- `0` (domyślnie) — **nie gromadzi** metadanych konwersji ani kopii plików
- `>0` — zapisuje metadane (nazwa pliku, firma, NIP, data) do bazy i archiwizuje XLSX przez N dni

## Przepływ konwersji

1. Użytkownik przesyła plik XML/XAdES
2. Walidacja reCAPTCHA (jeśli włączona)
3. Walidacja formatu i rozmiaru pliku (max 10 MB)
4. Walidacja XML (bezpieczeństwo, struktura, typ jednostki)
5. Konwersja XML → XLSX z disclaimerem
6. Wyodrębnienie załączników (jeśli są)
7. Generowanie tymczasowego linku (5 min)
8. Wyświetlenie wyniku z podglądem i kartami pobierania (XLSX + załączniki)
9. Po wygaśnięciu linku (5 min) — ładna strona z przyciskiem "Konwertuj ponownie"

## Generowane pliki XLSX

### Disclaimer
Każdy arkusz zawiera w wierszu 1 kursywny tekst:
> *Wygenerowano przez czytnik.analizy.io — narzędzie pomocnicze. Zweryfikuj poprawność danych przed wykorzystaniem.*

### Arkusze
- **Bilans** — aktywa i pasywa (bieżące, porównawcze, przekształcone)
- **RZiS** — wariant porównawczy lub kalkulacyjny
- **Nota podatkowa** — dodatkowe informacje i objaśnienia
- **Zestawienie zmian w kapitale** — zmiany w kapitale własnym
- **Przepływy** — metoda bezpośrednia lub pośrednia

## Docker

### Dockerfile.prod
- Bazowy obraz: `python:3.11-slim`
- Zależności systemowe: gcc, libxml2-dev, libxslt1-dev (dla lxml)
- Użytkownik non-root: `appuser` (bezpieczeństwo)
- Port: 8000, Workers: 1 (uvicorn — 1 worker, bo temp_files jest in-memory dict)
- Healthcheck: sprawdza `/docs`

### docker-compose.hostinger.yml (Traefik)
```yaml
services:
  web:
    container_name: czytnik-sf
    labels:
      - traefik.enable=true
      - traefik.http.routers.czytnik.rule=Host(`czytnik.analizy.io`)
      - traefik.http.routers.czytnik.tls=true
      - traefik.http.routers.czytnik.tls.certresolver=mytlschallenge
      - traefik.http.services.czytnik.loadbalancer.server.port=8000
      - traefik.docker.network=root_default
    networks:
      - traefik_network
    volumes:
      - czytnik_data:/app/data

networks:
  traefik_network:
    external: true
    name: root_default
```

## Bezpieczeństwo

1. **reCAPTCHA v2** — ochrona przed botami
2. **JWT w cookie HttpOnly** — sesja admina
3. **Bcrypt** — hashowanie haseł
4. **Walidacja XML** — ochrona przed XXE i innymi atakami
5. **Non-root user** — Docker uruchamia aplikację jako `appuser`
6. **Tymczasowe pliki** — automatyczne usuwanie po 5 minutach
7. **Brak gromadzenia danych** — metadane konwersji nie są zapisywane

## GDPR / Cookie Consent

Aplikacja zawiera baner cookie consent (ciemny styl):
- Dwa przyciski: "Akceptuję wszystkie" / "Tylko niezbędne"
- Google Analytics uruchamia się wyłącznie po akceptacji
- Zgoda zapisywana w localStorage (`cookie_consent`)
- Reset preferencji przez "Ustawienia cookies" w stopce

## Uruchomienie lokalne

```bash
cd web
pip install -r requirements.txt
python run_local.py
# lub: uvicorn app.main:app --reload --port 8000
```

Dostęp:
- Aplikacja: http://localhost:8000
- Panel admina: http://localhost:8000/admin/login
- Dokumentacja API: http://localhost:8000/docs

## Zarządzanie

### Tworzenie administratora
```bash
docker exec -it czytnik-sf python create_admin.py admin@example.com Haslo123
docker exec -it czytnik-sf python create_admin.py --list
```

## Historia wersji

| Wersja | Data | Zmiany |
|--------|------|--------|
| 3.0.0 | luty 2026 | Modernizacja UI (wzór: PPS Maker), modale, baner bezpieczeństwa, cookie consent, disclaimer w XLSX, wyłączenie gromadzenia danych, domena czytnik.analizy.io, karty pobierania, strona wygaśnięcia linku, favicon teal, 1 worker |
| 2.0.0 | grudzień 2025 | Uproszczenie: usunięcie rejestracji, publiczny dostęp z reCAPTCHA |
| 1.0.0 | listopad 2025 | Pierwsza wersja z rejestracją i logowaniem |

---

*Dokumentacja: luty 2026 | Domena: czytnik.analizy.io*
