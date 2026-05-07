# Czytnik SF - notatki dla Claude Code

## Stack
- **Backend:** FastAPI (Python) + SQLAlchemy (async, SQLite)
- **Frontend:** Jinja2 + HTMX + vanilla JS
- **Deploy:** Docker + Traefik na VPS Hostinger
- **URL produkcyjne:** https://czytnik.analizy.io/
- **Container produkcyjny:** `czytnik-sf`

## Struktura
- `app/main.py` - routes FastAPI
- `app/config.py` - Settings (pydantic), env vars
- `app/templates/` - Jinja2 (base.html, index.html, ...)
- `app/static/` - CSS/JS/favicon
- `docker-compose.hostinger.yml` - production compose (Traefik labels, env)

## Analityka (od 2026-05-07)
- **Umami** (cookieless, self-hosted na VPS) zamiast Google Analytics
- Snippet w `app/templates/base.html` (po `<link rel="apple-touch-icon">`)
- `data-website-id` = `21b7e0aa-b9b0-4105-9a0d-f84ffcaed2d0`
- Tracker: `https://t.analizy.io/script.js`
- GA wylaczone przez puste `GA_MEASUREMENT_ID` w docker-compose.hostinger.yml
- Kod GA pozostaje warunkowy w base.html (`{% if ga_measurement_id %}`) - mozna w przyszlosci wlaczyc dolozeniem wartosci do env var
- Polityka prywatnosci zaktualizowana (sekcja 2, 3 [B Umami + C GA opcjonalne], 5, 7)

## Deploy
- `git push origin main` → SSH na VPS:
  `ssh hostinger "cd /root/Konwersja-SF/web && git pull && docker compose -f docker-compose.hostinger.yml down && docker compose -f docker-compose.hostinger.yml up -d --build"`
- W razie konfliktu nazwy: `docker rm -f czytnik-sf` przed `up`
- Repo HTTPS, public - pull bez auth

## Konwencje
- Polski w UI i komentarzach
- GA_MEASUREMENT_ID i podobne ustawiane przez env w docker-compose, NIE hardcoded w kodzie
