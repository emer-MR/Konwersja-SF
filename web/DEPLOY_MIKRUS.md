# Deploy na mikr.us 3.0

Instrukcja wdrożenia Konwertera SF na serwer mikr.us 3.0 (2 GB RAM, 25 GB dysk).

## Wymagania wstępne

- Konto na mikr.us z aktywnym serwerem 3.0
- Dostęp SSH do serwera
- Domena (opcjonalnie) lub użycie portów mikr.us

---

## Krok 1: Połączenie z serwerem

```bash
# Dane dostępowe znajdziesz w panelu mikr.us
ssh użytkownik@srvXXX.mikr.us -p PORT_SSH
```

---

## Krok 2: Aktualizacja systemu i instalacja zależności

```bash
# Aktualizacja pakietów
sudo apt update && sudo apt upgrade -y

# Instalacja Python 3.11+ i narzędzi
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Sprawdź wersję Pythona (wymagana 3.10+)
python3 --version
```

---

## Krok 3: Utworzenie użytkownika aplikacji

```bash
# Utwórz dedykowanego użytkownika (bezpieczeństwo)
sudo useradd -m -s /bin/bash konwerter
sudo mkdir -p /home/konwerter/app
sudo chown konwerter:konwerter /home/konwerter/app
```

---

## Krok 4: Pobranie kodu aplikacji

```bash
# Przełącz na użytkownika aplikacji
sudo su - konwerter

# Sklonuj repozytorium
cd /home/konwerter
git clone https://github.com/emer-MR/Konwersja-SF.git app

# Lub jeśli repo prywatne - skopiuj pliki przez scp
```

---

## Krok 5: Konfiguracja środowiska Python

```bash
# Jako użytkownik konwerter
cd /home/konwerter/app/web

# Utwórz wirtualne środowisko
python3 -m venv venv

# Aktywuj środowisko
source venv/bin/activate

# Zainstaluj zależności
pip install --upgrade pip
pip install -r requirements.txt

# Zainstaluj również gunicorn (serwer produkcyjny)
pip install gunicorn uvicorn[standard]
```

---

## Krok 6: Konfiguracja zmiennych środowiskowych

```bash
# Utwórz plik .env
nano /home/konwerter/app/web/.env
```

Zawartość pliku `.env`:

```env
# WAŻNE: Wygeneruj losowy klucz!
# Możesz użyć: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=tutaj-wklej-wygenerowany-64-znakowy-klucz

# Baza danych
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# Ustawienia aplikacji
APP_NAME=Konwerter SF
MAX_CONVERSIONS_PER_DAY=10
MAX_UPLOAD_SIZE_MB=10
```

```bash
# Wygeneruj SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
# Skopiuj wynik do pliku .env
```

---

## Krok 7: Inicjalizacja katalogów

```bash
cd /home/konwerter/app/web

# Utwórz wymagane katalogi
mkdir -p data uploads output

# Ustaw uprawnienia
chmod 750 data uploads output
```

---

## Krok 8: Test uruchomienia

```bash
cd /home/konwerter/app/web
source venv/bin/activate

# Testowe uruchomienie
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Jeśli działa (zobaczysz "Uvicorn running on..."), zatrzymaj Ctrl+C
```

---

## Krok 9: Konfiguracja systemd (autostart)

```bash
# Wróć do głównego użytkownika
exit

# Utwórz plik serwisu
sudo nano /etc/systemd/system/konwerter.service
```

Zawartość pliku `konwerter.service`:

```ini
[Unit]
Description=Konwerter SF FastAPI
After=network.target

[Service]
User=konwerter
Group=konwerter
WorkingDirectory=/home/konwerter/app/web
Environment="PATH=/home/konwerter/app/web/venv/bin"
EnvironmentFile=/home/konwerter/app/web/.env
ExecStart=/home/konwerter/app/web/venv/bin/gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /home/konwerter/app/web/access.log \
    --error-logfile /home/konwerter/app/web/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Włącz i uruchom serwis
sudo systemctl daemon-reload
sudo systemctl enable konwerter
sudo systemctl start konwerter

# Sprawdź status
sudo systemctl status konwerter
```

---

## Krok 10: Konfiguracja Nginx (reverse proxy)

```bash
sudo nano /etc/nginx/sites-available/konwerter
```

Zawartość (bez SSL - na początek):

```nginx
server {
    listen 80;
    server_name _;  # lub twoja-domena.pl

    client_max_body_size 15M;  # Limit uploadu

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }
}
```

```bash
# Aktywuj konfigurację
sudo ln -s /etc/nginx/sites-available/konwerter /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Usuń domyślną stronę

# Sprawdź konfigurację
sudo nginx -t

# Zrestartuj Nginx
sudo systemctl restart nginx
```

---

## Krok 11: Konfiguracja portów mikr.us

W panelu mikr.us masz przypisane 2 porty IPv4. Skonfiguruj przekierowanie:

1. Zaloguj się do panelu mikr.us
2. Znajdź przypisane porty (np. 12345, 12346)
3. Port 12345 → przekieruj na port 80 (HTTP)
4. Port 12346 → przekieruj na port 443 (HTTPS) - jeśli używasz SSL

**Dostęp do aplikacji:**
```
http://srvXXX.mikr.us:12345
```

---

## Krok 12: SSL z Let's Encrypt (opcjonalnie, wymaga domeny)

Jeśli masz własną domenę:

```bash
# Dodaj domenę do Nginx (zmień server_name)
sudo nano /etc/nginx/sites-available/konwerter
# Zmień: server_name twoja-domena.pl;

# Uzyskaj certyfikat
sudo certbot --nginx -d twoja-domena.pl

# Certbot automatycznie skonfiguruje SSL i odnowi certyfikat
```

---

## Krok 13: Konfiguracja zapory (UFW)

```bash
# Włącz UFW
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Sprawdź status
sudo ufw status
```

---

## Aktualizacja aplikacji

```bash
# Jako użytkownik konwerter
sudo su - konwerter
cd /home/konwerter/app

# Pobierz zmiany
git pull origin main

# Aktywuj venv i zaktualizuj zależności
cd web
source venv/bin/activate
pip install -r requirements.txt

# Wróć do głównego użytkownika i zrestartuj serwis
exit
sudo systemctl restart konwerter
```

---

## Przydatne komendy

```bash
# Status aplikacji
sudo systemctl status konwerter

# Logi aplikacji
tail -f /home/konwerter/app/web/error.log
tail -f /home/konwerter/app/web/access.log

# Logi systemowe
sudo journalctl -u konwerter -f

# Restart aplikacji
sudo systemctl restart konwerter

# Restart Nginx
sudo systemctl restart nginx

# Sprawdź zużycie RAM
free -h

# Sprawdź zużycie dysku
df -h
```

---

## Rozwiązywanie problemów

### Aplikacja nie startuje

```bash
# Sprawdź logi
sudo journalctl -u konwerter -n 50

# Sprawdź czy port 8000 jest wolny
sudo netstat -tlnp | grep 8000

# Testowe uruchomienie ręczne
sudo su - konwerter
cd /home/konwerter/app/web
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Błąd 502 Bad Gateway

```bash
# Sprawdź czy aplikacja działa
sudo systemctl status konwerter

# Sprawdź logi Nginx
sudo tail -f /var/log/nginx/error.log
```

### Brak pamięci (OOM)

```bash
# Sprawdź zużycie
free -h
htop

# Zmniejsz liczbę workerów w konwerter.service
# --workers 2 → --workers 1
sudo nano /etc/systemd/system/konwerter.service
sudo systemctl daemon-reload
sudo systemctl restart konwerter
```

---

## Struktura na serwerze

```
/home/konwerter/
└── app/
    ├── src/                 # Parser XML (z głównego projektu)
    ├── web/
    │   ├── venv/            # Środowisko wirtualne Python
    │   ├── app/             # Kod aplikacji FastAPI
    │   ├── data/            # Baza SQLite
    │   ├── uploads/         # Pliki tymczasowe (upload)
    │   ├── output/          # Wygenerowane XLSX
    │   ├── .env             # Zmienne środowiskowe (nie w git!)
    │   ├── access.log       # Logi dostępu
    │   └── error.log        # Logi błędów
    └── ...
```

---

## Checklist przed uruchomieniem produkcyjnym

- [ ] SECRET_KEY ustawiony w .env (losowy, 64+ znaki)
- [ ] Uprawnienia plików (750 dla katalogów z danymi)
- [ ] Firewall włączony (UFW)
- [ ] SSL/HTTPS skonfigurowany (jeśli domena)
- [ ] Backup bazy danych (cron)
- [ ] Monitoring (opcjonalnie: uptimerobot.com)

---

*Instrukcja dla mikr.us 3.0 - 28.11.2025*
