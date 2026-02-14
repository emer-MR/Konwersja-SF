# Czytnik SF - Wersja Webowa

Bezpłatna aplikacja webowa do konwersji polskich e-Sprawozdań finansowych XML na Excel (XLSX).

**Domena produkcyjna:** https://czytnik.analizy.io

## Funkcjonalności

- Upload plików XML/XAdES (e-Sprawozdania, max 10 MB)
- Konwersja do XLSX — Bilans, RZiS, Nota podatkowa, Zestawienie zmian, Przepływy
- Obsługa jednostek: Mikro, Mała, Inna (schematy v1-0, v1-2, v1-3)
- Wyodrębnianie załączników PDF z XML
- Disclaimer informacyjny w generowanych plikach
- Google reCAPTCHA v2 (ochrona antyspamowa)
- Google Analytics z GDPR cookie consent
- Brak gromadzenia danych o konwersjach (prywatność)

## Stack technologiczny

- **Backend:** FastAPI + Uvicorn (Python 3.11)
- **Baza danych:** SQLite (async) — tylko konta admin
- **Frontend:** Jinja2 + HTMX (self-contained CSS)
- **Konteneryzacja:** Docker + Traefik (Hostinger VPS)

## Uruchomienie lokalne

```bash
cd web
pip install -r requirements.txt
python run_local.py
```

Lub bezpośrednio:
```bash
uvicorn app.main:app --reload --port 8000
```

Dostęp:
- Aplikacja: http://localhost:8000
- Panel admina: http://localhost:8000/admin/login
- Dokumentacja API: http://localhost:8000/docs

## Deployment (Hostinger VPS)

```bash
ssh root@72.62.1.15
cd /docker/konwersja-sf
git pull origin main
cd web
docker compose -f docker-compose.hostinger.yml up --build -d
```

Szczegóły: [deployment-czytnik-ok.md](deployment-czytnik-ok.md)

## Konfiguracja

Skopiuj `.env.example` jako `.env` i uzupełnij:

```bash
cp .env.example .env
```

Kluczowe zmienne:
- `SECRET_KEY` — wygeneruj: `openssl rand -hex 32`
- `RECAPTCHA_SITE_KEY` / `RECAPTCHA_SECRET_KEY` — klucze reCAPTCHA
- `GA_MEASUREMENT_ID` — Google Analytics (domyślnie: G-BD3959F2HL)
- `ADMIN_FILE_RETENTION_DAYS` — 0 = nie gromadź danych o konwersjach (domyślnie)

## Struktura projektu

```
web/
├── app/
│   ├── main.py              # Główna aplikacja FastAPI
│   ├── config.py            # Konfiguracja (pydantic-settings)
│   ├── converter_simple.py  # Konwerter XML → XLSX
│   ├── xml_validator.py     # Walidacja XML
│   ├── database.py          # SQLAlchemy async
│   ├── models.py            # Modele (User, Conversion)
│   ├── auth.py              # Autentykacja JWT
│   ├── templates/
│   │   ├── base.html        # Szablon bazowy (CSS + modale + JS)
│   │   ├── index.html       # Strona konwersji
│   │   └── partials/        # Fragmenty HTMX
│   └── static/
├── docker-compose.hostinger.yml  # Hostinger VPS z Traefik
├── Dockerfile.prod               # Kontener produkcyjny
├── requirements.txt
├── run_local.py
└── .env.example
```

## Dokumentacja

- [dokumentacja-czytnik-ok.md](dokumentacja-czytnik-ok.md) — pełna dokumentacja techniczna
- [deployment-czytnik-ok.md](deployment-czytnik-ok.md) — procedury wdrożenia i aktualizacji
- [DEPLOY_HOSTINGER_VPS.md](DEPLOY_HOSTINGER_VPS.md) — szczegółowy przewodnik Hostinger VPS
