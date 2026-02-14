# Deployment Czytnik SF na Hostinger VPS

## Informacje o serwerze

- **Serwer:** Hostinger VPS
- **IP:** 72.62.1.15
- **SSH:** `ssh root@72.62.1.15`
- **Reverse Proxy:** Traefik (działa w sieci `root_default`)
- **Domena:** czytnik.analizy.io

## Struktura katalogów na serwerze

```
/root/
└── Konwersja-SF/          # git clone (repo GitHub)
    ├── web/
    │   ├── docker-compose.hostinger.yml   # UŻYWANY PLIK COMPOSE
    │   ├── Dockerfile.prod
    │   ├── .env                           # Zmienne środowiskowe
    │   └── app/
    └── src/
```

## Konfiguracja .env

Plik `.env` w katalogu `/root/Konwersja-SF/web/`:

```env
# WYMAGANE
SECRET_KEY=wygenerowany-klucz-32-znaki-hex
RECAPTCHA_SITE_KEY=klucz-z-google-recaptcha
RECAPTCHA_SECRET_KEY=secret-z-google-recaptcha

# OPCJONALNE (mają wartości domyślne)
GA_MEASUREMENT_ID=G-BD3959F2HL
CONTACT_EMAIL=kontakt@analizy.io
ADMIN_FILE_RETENTION_DAYS=0
MAX_UPLOAD_SIZE_MB=15
DEBUG=false
```

### Generowanie SECRET_KEY

```bash
openssl rand -hex 32
# lub Python:
python -c "import secrets; print(secrets.token_hex(32))"
```

## Procedura wdrożenia (pierwszy raz)

```bash
# 1. Połącz się z serwerem
ssh root@72.62.1.15

# 2. Utwórz katalog i sklonuj repo
mkdir -p /docker
cd /docker
git clone https://github.com/emer-MR/Konwersja-SF.git konwersja-sf
cd konwersja-sf/web

# 3. Utwórz plik .env
nano .env
# (wklej konfigurację z sekcji powyżej)

# 4. Uruchom kontener
docker compose -f docker-compose.hostinger.yml up --build -d

# 5. Poczekaj na start (15 sekund)
sleep 15

# 6. (Opcjonalnie) Utwórz konto admina
docker exec -it czytnik-sf python create_admin.py admin@example.com TwojeHaslo123

# 7. Sprawdź logi
docker logs czytnik-sf
```

## Procedura aktualizacji

```bash
# 1. Połącz się z serwerem
ssh root@72.62.1.15

# 2. Przejdź do katalogu
cd /root/Konwersja-SF

# 3. Pobierz zmiany
git pull origin main

# 4. Przebuduj i uruchom
cd web
docker compose -f docker-compose.hostinger.yml up --build -d

# 5. Sprawdź logi
docker logs -f czytnik-sf
```

## Procedura aktualizacji z resetem bazy danych

Użyj gdy zmieniła się struktura bazy:

```bash
ssh root@72.62.1.15
cd /root/Konwersja-SF

git pull origin main

cd web
docker compose -f docker-compose.hostinger.yml down

# Usuń wolumen z bazą (UWAGA: usuwa dane!)
docker volume rm web_czytnik_data 2>/dev/null || docker volume rm konwersja-sf_czytnik_data 2>/dev/null || true

docker compose -f docker-compose.hostinger.yml up --build -d

sleep 15
docker exec -it czytnik-sf python create_admin.py admin@example.com TwojeHaslo123
```

## Diagnostyka

### Sprawdź status kontenera
```bash
docker ps -a | grep czytnik
```

### Logi aplikacji
```bash
docker logs czytnik-sf
docker logs -f czytnik-sf  # Na żywo
```

### Wejdź do kontenera
```bash
docker exec -it czytnik-sf /bin/bash
```

### Sprawdź sieć Traefik
```bash
docker network ls | grep root
docker network inspect root_default
```

### Sprawdź wolumeny
```bash
docker volume ls | grep czytnik
```

## Kluczowe elementy docker-compose.hostinger.yml

```yaml
services:
  web:
    build:
      context: ..
      dockerfile: web/Dockerfile.prod
    container_name: czytnik-sf

    # TRAEFIK - kluczowe dla działania domeny
    labels:
      - traefik.enable=true
      - traefik.http.routers.czytnik.rule=Host(`czytnik.analizy.io`)
      - traefik.http.routers.czytnik.tls=true
      - traefik.http.routers.czytnik.entrypoints=web,websecure
      - traefik.http.routers.czytnik.tls.certresolver=mytlschallenge
      - traefik.http.services.czytnik.loadbalancer.server.port=8000
      - traefik.docker.network=root_default

    networks:
      - default
      - traefik_network

networks:
  traefik_network:
    external: true
    name: root_default
```

## Uwagi

1. **Nazwa kontenera** — `czytnik-sf` (unikalna na serwerze)
2. **Nazwa routera Traefik** — `czytnik` (unikalna)
3. **Wolumen** — `czytnik_data` (persistentny)
4. **Port wewnętrzny** — 8000 (Traefik przekierowuje)
5. **Sieć** — `root_default` (external)
6. **SSL** — automatycznie przez Traefik + Let's Encrypt

## Checklist przed deploymentem

- [ ] Rekord DNS A: `czytnik` → IP serwera (72.62.1.15)
- [ ] Plik `.env` z SECRET_KEY i kluczami reCAPTCHA
- [ ] `git pull` — najnowszy kod
- [ ] `docker compose up --build -d` — kontener działa
- [ ] `docker logs czytnik-sf` — brak błędów
- [ ] https://czytnik.analizy.io — strona dostępna

---

*Dokumentacja: luty 2026 | Domena: czytnik.analizy.io*
