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
- Alias `ssh hostinger` nie działa na maszynach z `ł` w profilu - pełna forma:
  `ssh -o StrictHostKeyChecking=no -i ~/.ssh/hostinger_vps root@72.62.1.15 "..."`
- Na VPS `web/docker-compose.hostinger.yml` ma **lokalną, niecommitowaną zmianę** (healthcheck
  `interval: 120s`, `cpus: "1.0"`) oraz `.env` w katalogu repo - `git pull --ff-only` je zachowuje,
  nie robić `git reset --hard` / `git checkout .` na serwerze.
- **Po każdym deployu sprawdzić** (to nie jest opcjonalne - kontener potrafi wstać i od razu paść):
  `docker ps --filter name=czytnik-sf` (musi być `healthy`, nie `Restarting`),
  `docker logs --tail 20 czytnik-sf`, `curl -s -o /dev/null -w "%{http_code}" https://czytnik.analizy.io/` (200).

## Smoke test po deployu (bez dotykania produkcji)
`web/tests/smoke_test.py` - uruchamiany w **tymczasowym kontenerze** z obrazu `web-web:latest`
(osobna baza w `/tmp`, reCAPTCHA wyłączona, brak sieci; wolumen produkcyjny tylko do odczytu -
sprawdza, czy bcrypt czyta istniejące hashe). Sprawdza: strony publiczne, konwersję każdego
`*.xml` z `/tmp/smoke/`, pobranie XLSX, błędny XML → komunikat, logowanie admina (złe/dobre hasło), `/admin`.
Z Windowsa (katalog z `smoke_test.py` i kilkoma próbkami XML):
```bash
cd <katalog> && tar -cf - *.xml smoke_test.py | ssh -o StrictHostKeyChecking=no -i ~/.ssh/hostinger_vps root@72.62.1.15 \
  "docker run --rm -i --network none -e DATABASE_URL=sqlite+aiosqlite:////tmp/smoke.db -e RECAPTCHA_ENABLED=false \
   -e SECRET_KEY=smoke-test -e ADMIN_FILE_RETENTION_DAYS=0 -v web_czytnik_data:/prod:ro --entrypoint sh web-web:latest \
   -c 'mkdir -p /tmp/smoke && cd /tmp/smoke && tar -xf - && mv smoke_test.py smoke.py && cd /app && python /tmp/smoke/smoke.py'"
```
Oczekiwany wynik: `WYNIK: WSZYSTKO OK` (2026-09-25: 17/17). Próbki XML nie są w repo (dane klientów) -
brać z `[Legacy]\...\Przykłady sprawozdań` lub z folderu sprawy; dla formatu 2025 (`Dokument`) dołączyć SF za 2025.

## Zależności - wersje przypięte (od 2026-09-25)
- `requirements.txt` ma **dokładne wersje** (`==`), zdjęte `pip freeze` z działającego obrazu.
  Powód: przy samych `>=` przebudowa obrazu 2026-09-25 wciągnęła SQLAlchemy 2.1.0, które nie
  instaluje już `greenlet` - `sqlalchemy.ext.asyncio` rzucał ImportError, kontener restartował
  się w pętli, strona zwracała 404 (ok. 15 min przestoju). Stary obraz miał 2 miesiące i działał
  tylko dlatego, że nie był przebudowywany.
- Aktualizacja zależności = świadoma zmiana: podbić wersję w `requirements.txt`, przed deployem
  sprawdzić start na zbudowanym obrazie bez ruszania produkcji, np.
  `docker compose -f docker-compose.hostinger.yml build && docker run --rm --entrypoint sh web-web:latest -c "cd /app && python -c 'import app.main'"`.
- `starlette` celowo < 0.46 (stara sygnatura `TemplateResponse`), obecnie 0.45.3.
- Web używa wspólnego `../src/parser.py` (Dockerfile.prod: `COPY src ./src`) - zmiany w parserze
  wymagają przebudowy obrazu; `indicators.py`/`multi_converter.py` web nie używa.

## Konwencje
- Polski w UI i komentarzach
- GA_MEASUREMENT_ID i podobne ustawiane przez env w docker-compose, NIE hardcoded w kodzie
