# Deploy Konwertera SF na Hostinger VPS z Docker Manager

## Spis treści
1. [Wymagania](#wymagania)
2. [Opcja A: Przez Hostinger Docker Manager (GUI)](#opcja-a-przez-hostinger-docker-manager-gui)
3. [Opcja B: Przez SSH (tradycyjna metoda)](#opcja-b-przez-ssh-tradycyjna-metoda)
4. [Konfiguracja domeny i SSL](#konfiguracja-domeny-i-ssl)
5. [Utworzenie konta admina](#utworzenie-konta-admina)
6. [Zarządzanie i monitoring](#zarządzanie-i-monitoring)

---

## Wymagania

### Przed rozpoczęciem przygotuj:
- [ ] VPS Hostinger z Docker Manager
- [ ] Domenę wskazującą na IP VPS
- [ ] Klucze reCAPTCHA v2 z https://www.google.com/recaptcha/admin

### Wygeneruj SECRET_KEY (lokalnie)
```bash
# Windows PowerShell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# lub Linux/Mac
openssl rand -hex 32
```

Zapisz wygenerowany klucz - będzie potrzebny w konfiguracji.

---

## Opcja A: Przez Hostinger Docker Manager (GUI)

### Krok 1: Przygotowanie pliku docker-compose

Hostinger Docker Manager może pobrać konfigurację bezpośrednio z URL. Musisz najpierw stworzyć plik `docker-compose.hostinger.yml` i wrzucić go do repozytorium.

**Plik jest już przygotowany:** `web/docker-compose.hostinger.yml`

### Krok 2: Dostęp do Docker Manager

1. Zaloguj się do panelu Hostinger
2. Przejdź do: **Pulpit VPS → Docker Manager**

### Krok 3: Wdrożenie przez URL

1. Kliknij **"Deploy new project"** lub **"Compose from URL"**
2. Wklej URL do pliku docker-compose:
   ```
   https://raw.githubusercontent.com/emer-MR/Konwersja-SF/main/web/docker-compose.hostinger.yml
   ```
3. Uzupełnij zmienne środowiskowe w formularzu:
   - `SECRET_KEY` = wygenerowany wcześniej klucz
   - `RECAPTCHA_SITE_KEY` = Twój klucz strony reCAPTCHA
   - `RECAPTCHA_SECRET_KEY` = Twój klucz tajny reCAPTCHA

### Krok 4: Konfiguracja portów

W sekcji **Ports** ustaw:
```
8080:8000
```

To oznacza: port 8000 kontenera będzie dostępny jako port 8080 na VPS.

### Krok 5: Deploy

1. Kliknij **"Deploy"**
2. Poczekaj 1-2 minuty na pobranie obrazu i uruchomienie
3. Sprawdź status w liście projektów

### Krok 6: Weryfikacja

Otwórz w przeglądarce:
```
http://TWOJE_IP_VPS:8080
```

---

## Opcja B: Przez SSH (tradycyjna metoda)

Jeśli wolisz pełną kontrolę lub Docker Manager nie działa.

### Krok 1: Połącz się przez SSH

```bash
ssh root@TWOJE_IP_VPS
```

### Krok 2: Utwórz katalog i pobierz projekt

```bash
mkdir -p ~/konwerter-sf
cd ~/konwerter-sf
git clone https://github.com/emer-MR/Konwersja-SF.git .
cd web
```

### Krok 3: Utwórz plik .env

```bash
cat > .env << 'EOF'
SECRET_KEY=WKLEJ_WYGENEROWANY_KLUCZ
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
MAX_CONVERSIONS_PER_DAY=20
MAX_UPLOAD_SIZE_MB=15
RECAPTCHA_SITE_KEY=TWOJ_SITE_KEY
RECAPTCHA_SECRET_KEY=TWOJ_SECRET_KEY
DEBUG=false
EOF
```

Edytuj plik i uzupełnij wartości:
```bash
nano .env
```

### Krok 4: Zbuduj i uruchom

```bash
docker compose -f docker-compose.hostinger.yml build
docker compose -f docker-compose.hostinger.yml up -d
```

### Krok 5: Sprawdź status

```bash
docker compose -f docker-compose.hostinger.yml ps
docker compose -f docker-compose.hostinger.yml logs -f
```

---

## Konfiguracja domeny i SSL

### Opcja 1: Nginx na VPS (zalecane)

#### Instalacja Nginx

```bash
apt update
apt install -y nginx certbot python3-certbot-nginx
```

#### Konfiguracja

```bash
nano /etc/nginx/sites-available/konwerter-sf
```

Wklej (zamień domenę):

```nginx
server {
    listen 80;
    server_name konwerter.twojadomena.pl;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        client_max_body_size 20M;
    }
}
```

#### Aktywacja

```bash
ln -s /etc/nginx/sites-available/konwerter-sf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

#### Certyfikat SSL

```bash
certbot --nginx -d konwerter.twojadomena.pl
```

### Opcja 2: Cloudflare (prostsze)

1. Przenieś domenę do Cloudflare (lub dodaj jako zewnętrzną)
2. Ustaw rekord A: `konwerter` → IP VPS
3. Włącz Proxy (pomarańczowa chmurka)
4. SSL/TLS → Full

Cloudflare automatycznie zapewni SSL.

---

## Utworzenie konta admina

### Przez SSH

```bash
# Wejdź do kontenera
docker exec -it konwerter-sf bash

# Utwórz admina
cd /app
python create_admin.py admin@twojadomena.pl TwojeHaslo123

# Wyjdź
exit
```

### Przez Docker Manager

W panelu Hostinger Docker Manager:
1. Znajdź projekt "konwerter-sf"
2. Kliknij na kontener
3. Użyj funkcji "Terminal" lub "Exec"
4. Wykonaj: `python create_admin.py admin@twojadomena.pl TwojeHaslo123`

---

## Zarządzanie i monitoring

### Komendy Docker (przez SSH)

```bash
cd ~/konwerter-sf/web

# Status
docker compose -f docker-compose.hostinger.yml ps

# Logi
docker compose -f docker-compose.hostinger.yml logs -f

# Restart
docker compose -f docker-compose.hostinger.yml restart

# Stop
docker compose -f docker-compose.hostinger.yml down

# Aktualizacja
git pull
docker compose -f docker-compose.hostinger.yml build
docker compose -f docker-compose.hostinger.yml up -d
```

### Przez Docker Manager (GUI)

- **Edit** - modyfikuj konfigurację
- **Stop/Start** - kontroluj stan
- **Logs** - przeglądaj logi
- **Delete** - usuń projekt

### Backup bazy

```bash
# Ręczny backup
docker cp konwerter-sf:/app/data/app.db ~/backup_$(date +%Y%m%d).db

# Automatyczny (cron)
crontab -e
# Dodaj:
0 3 * * * docker cp konwerter-sf:/app/data/app.db ~/backups/app_$(date +\%Y\%m\%d).db
```

---

## Troubleshooting

### Aplikacja nie startuje
```bash
docker compose -f docker-compose.hostinger.yml logs
```

### Błąd 502 Bad Gateway
```bash
# Sprawdź czy kontener działa
docker ps

# Sprawdź czy port jest otwarty
curl http://localhost:8080
```

### Brak miejsca na dysku
```bash
# Usuń nieużywane obrazy
docker system prune -a
```

### Za mało RAM
```bash
# Sprawdź zużycie
docker stats --no-stream
```

---

## Podsumowanie

| Krok | Opcja A (GUI) | Opcja B (SSH) |
|------|---------------|---------------|
| 1 | Docker Manager → Deploy | SSH → git clone |
| 2 | Wklej URL do compose | Utwórz .env |
| 3 | Uzupełnij zmienne | docker compose up |
| 4 | Kliknij Deploy | Nginx + certbot |
| 5 | Nginx + SSL | Utwórz admina |

---

*Dokumentacja: 01.12.2024*
