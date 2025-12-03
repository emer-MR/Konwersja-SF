# Deploy na mikr.us - Docker obok istniejących aplikacji

*Do rozważenia i powrotu w przyszłości*

---

## Kontekst

Na serwerze mikr.us 3.0 (2 GB RAM, 25 GB dysk) działa już Docker z inną aplikacją. Rozważamy deploy Konwertera SF jako kolejny kontener.

---

## Opcje deployu

| Opcja | Zalety | Wady |
|-------|--------|------|
| **Docker (zalecana)** | Spójność z istniejącą infrastrukturą, izolacja, łatwy restart | +50-100 MB RAM overhead |
| Natywnie obok Dockera | Mniej RAM | Dwa różne systemy do zarządzania, chaos |

**Rekomendacja:** Zostać przy Dockerze dla spójności.

---

## Szacowane zużycie RAM

```
System + Docker daemon     ~200 MB
Istniejąca aplikacja       ~??? MB (do sprawdzenia)
Konwerter SF (Docker)      ~250-350 MB
─────────────────────────────────────
Razem                      ~500-600 MB + istniejąca apka
```

Przy 2 GB RAM powinno się zmieścić 2-3 lekkie aplikacje.

---

## Architektura wielu serwisów na jednym serwerze

```
Internet → Nginx/Traefik (port 80/443) → routing po domenie
                                            ├── app1.domena.pl → kontener A
                                            ├── konwerter.domena.pl → kontener B (Konwerter SF)
                                            └── app3.domena.pl → kontener C
```

---

## Pytania do ustalenia przed deployem

### 1. Jaki reverse proxy jest używany?

- [ ] **Nginx** (osobny kontener lub na hoście)
- [ ] **Traefik** (automatyczne SSL, popularne z Docker)
- [ ] **Nginx Proxy Manager** (GUI do zarządzania)
- [ ] **Caddy** (automatyczne SSL)
- [ ] Inny: _______________

### 2. Jak zarządzane są kontenery?

- [ ] **docker-compose** (pliki YAML)
- [ ] **Portainer** (GUI webowe)
- [ ] **Ręcznie** (docker run)
- [ ] Inny: _______________

### 3. Jak rozwiązana jest kwestia domen/portów?

- [ ] **Własna domena** z subdomenami (np. app.mojadomena.pl)
- [ ] **Porty mikr.us** (srvXXX.mikr.us:PORT)
- [ ] **Cloudflare** jako proxy (darmowe SSL + ukrycie IP)
- [ ] Inny: _______________

### 4. Ile RAM zajmuje istniejąca aplikacja?

```bash
# Sprawdź komendą:
docker stats --no-stream
```

Wynik: _______________ MB

---

## Przykładowe konfiguracje (do dostosowania)

### Wariant A: docker-compose + Traefik

```yaml
# docker-compose.yml
version: '3.8'

services:
  konwerter:
    build: ./web
    container_name: konwerter-sf
    restart: unless-stopped
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.konwerter.rule=Host(`konwerter.mojadomena.pl`)"
      - "traefik.http.routers.konwerter.tls.certresolver=letsencrypt"
    networks:
      - proxy

networks:
  proxy:
    external: true
```

### Wariant B: docker-compose + Nginx Proxy Manager

```yaml
# docker-compose.yml
version: '3.8'

services:
  konwerter:
    build: ./web
    container_name: konwerter-sf
    restart: unless-stopped
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    expose:
      - "8000"
    networks:
      - npm_network

networks:
  npm_network:
    external: true
```

Potem w Nginx Proxy Manager dodać Proxy Host:
- Domain: konwerter.mojadomena.pl
- Forward: konwerter-sf:8000
- SSL: Request new certificate

### Wariant C: Osobny Nginx na hoście

```yaml
# docker-compose.yml
version: '3.8'

services:
  konwerter:
    build: ./web
    container_name: konwerter-sf
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"  # Tylko lokalnie
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
```

Nginx na hoście:
```nginx
# /etc/nginx/sites-available/konwerter
server {
    listen 80;
    server_name konwerter.mojadomena.pl;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Ograniczenia mikr.us do pamiętania

| Zasób | Limit | Rozwiązanie |
|-------|-------|-------------|
| **2 porty IPv4** | HTTP + HTTPS | Używaj domen + reverse proxy |
| **IPv6** | Bez limitu | Pełna konfiguracja możliwa |
| **2 GB RAM** | ~1.5 GB dla aplikacji | Monitoruj `docker stats` |
| **25 GB dysk** | Baza + pliki | Ustaw rotację logów i cleanup starych plików |

---

## Następne kroki

1. [ ] Sprawdzić jaki reverse proxy jest obecnie używany
2. [ ] Sprawdzić zużycie RAM istniejącej aplikacji
3. [ ] Zdecydować o domenie/subdomenach
4. [ ] Dostosować docker-compose.yml do istniejącej konfiguracji
5. [ ] Wdrożyć i przetestować

---

## Przydatne komendy diagnostyczne

```bash
# Sprawdź zużycie RAM przez kontenery
docker stats --no-stream

# Lista działających kontenerów
docker ps

# Logi kontenera
docker logs konwerter-sf -f

# Wolne miejsce na dysku
df -h

# Wolna pamięć RAM
free -h
```

---

*Notatka utworzona: 28.11.2025*
*Status: Do ustalenia - wymaga informacji o obecnej konfiguracji Docker*
