# Dokumentacja - Konwerter SF Online

## Podsumowanie prac (28.11.2025)

### Co zostało zrobione

#### 1. Aplikacja webowa FastAPI
Utworzono kompletną aplikację webową do konwersji sprawozdań finansowych XML na XLSX.

**Stos technologiczny:**
- **Backend:** FastAPI (async Python)
- **Frontend:** HTMX + Jinja2 + Pico CSS (bez JavaScript)
- **Baza danych:** SQLite z SQLAlchemy (async)
- **Autentykacja:** JWT tokeny + bcrypt
- **Konteneryzacja:** Docker + docker-compose

**Struktura projektu:**
```
web/
├── app/
│   ├── main.py              # Główna aplikacja FastAPI
│   ├── config.py            # Konfiguracja (pydantic-settings)
│   ├── database.py          # SQLAlchemy async
│   ├── models.py            # Modele User, Conversion
│   ├── schemas.py           # Schematy Pydantic
│   ├── auth.py              # Autentykacja JWT + bcrypt
│   ├── converter_simple.py  # Uproszczony konwerter (Bilans + RZiS)
│   ├── api/
│   │   ├── auth_routes.py   # Endpointy API autentykacji
│   │   └── convert_routes.py # Endpointy API konwersji (wyłączone)
│   └── templates/
│       ├── base.html        # Szablon bazowy
│       ├── index.html       # Strona główna
│       ├── login.html       # Logowanie
│       ├── register.html    # Rejestracja
│       ├── convert.html     # Strona konwersji
│       └── partials/        # Fragmenty HTMX
│           ├── conversion_result.html
│           ├── history_table.html
│           └── limit_badge.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_local.py             # Uruchomienie lokalne
└── README.md
```

#### 2. Funkcjonalności

| Funkcja | Opis |
|---------|------|
| Rejestracja | Tworzenie konta z email + hasło (min. 8 znaków) |
| Logowanie | JWT token w httponly cookie (24h) |
| Upload plików | Drag & drop, akceptuje .xml i .xades (max 10 MB) |
| Konwersja | XML e-Sprawozdanie → XLSX (Bilans + RZiS) |
| Limit dzienny | 10 konwersji na użytkownika dziennie |
| Historia | Lista ostatnich 20 konwersji z możliwością pobrania |
| Nazwy plików | Czytelny format: `SF_2023_NazwaFirmy.xlsx` |

#### 3. Naprawione błędy

1. **Kompatybilność bcrypt z Python 3.14**
   - Problem: `passlib` niekompatybilny z nową wersją bcrypt
   - Rozwiązanie: Bezpośrednie użycie biblioteki `bcrypt`

2. **JSON zamiast HTML w HTMX**
   - Problem: Endpointy zwracały JSON zamiast fragmentów HTML
   - Rozwiązanie: Zmiana ścieżek na `/htmx/*` i wyłączenie JSON routera

#### 4. Repozytorium
Kod dostępny na GitHub: https://github.com/emer-MR/Konwersja-SF

---

## Obecny stan bezpieczeństwa

### Co jest zaimplementowane

| Zabezpieczenie | Status | Opis |
|----------------|--------|------|
| Hashowanie haseł | ✅ | bcrypt z automatycznym saltem |
| JWT tokeny | ✅ | Podpisane tokenem, wygasają po 24h |
| HttpOnly cookies | ✅ | Token niedostępny dla JavaScript |
| SameSite cookies | ✅ | Ochrona przed CSRF (lax) |
| Walidacja rozszerzeń | ✅ | Tylko .xml i .xades |
| Limit rozmiaru | ✅ | Max 10 MB na plik |
| Limit dzienny | ✅ | 10 konwersji/użytkownik/dzień |
| Walidacja hasła | ✅ | Minimum 8 znaków |

### Co wymaga poprawy (przed produkcją)

| Problem | Priorytet | Ryzyko |
|---------|-----------|--------|
| SECRET_KEY hardcoded | 🔴 Krytyczny | Atakujący może podrobić tokeny JWT |
| Brak HTTPS | 🔴 Krytyczny | Hasła przesyłane plain-text |
| Brak rate limiting | 🟠 Wysoki | Brute-force na logowanie |
| Brak walidacji XML | 🟠 Wysoki | XXE injection |
| Brak security headers | 🟡 Średni | XSS, clickjacking |
| Brak logowania zdarzeń | 🟡 Średni | Brak audytu |

---

## Plan zabezpieczeń

### Etap 1: Krytyczne (przed uruchomieniem)

#### 1.1 SECRET_KEY w zmiennych środowiskowych

```python
# config.py - zmienić na:
SECRET_KEY: str  # bez wartości domyślnej
```

```bash
# .env (nie commitować!)
SECRET_KEY=wygeneruj-losowy-klucz-64-znaki
```

#### 1.2 Plik .gitignore

```gitignore
.env
*.db
data/
uploads/
output/
__pycache__/
*.pyc
```

#### 1.3 HTTPS na Synology

Skonfigurować reverse proxy z Let's Encrypt w DSM:
1. Control Panel → Application Portal → Reverse Proxy
2. Dodać certyfikat SSL (Let's Encrypt)
3. Przekierować HTTPS → kontener Docker

#### 1.4 Rate limiting

```python
# requirements.txt
slowapi>=0.1.9

# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # max 5 prób logowania na minutę
async def login_submit(...):
    ...
```

### Etap 2: Zalecane

#### 2.1 Security headers

```python
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

#### 2.2 Walidacja XML (ochrona przed XXE)

```python
from lxml import etree

def safe_parse_xml(xml_path: Path) -> etree._Element:
    """Bezpieczne parsowanie XML bez external entities."""
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        dtd_validation=False,
        load_dtd=False,
    )
    return etree.parse(str(xml_path), parser)
```

#### 2.3 Logowanie zdarzeń

```python
import logging

logging.basicConfig(
    filename="security.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Logować: nieudane logowania, przekroczone limity, błędy walidacji
```

---

## Wariant bez logowania

### Analiza

Rozważany jest wariant publiczny bez rejestracji/logowania.

#### Zalety
- Niższy próg wejścia dla użytkowników
- Prostszy interfejs
- Brak zarządzania kontami

#### Wady i ryzyka

| Ryzyko | Opis | Mitigacja |
|--------|------|-----------|
| Nadużycie zasobów | Boty mogą masowo konwertować pliki | CAPTCHA + rate limiting po IP |
| Brak historii | Użytkownik nie ma dostępu do poprzednich konwersji | Jednorazowy link do pobrania |
| Spam/DDoS | Łatwiejszy atak na serwer | Agresywny rate limiting |
| Brak audytu | Nie wiadomo kto używa serwisu | Logowanie IP (RODO!) |

### Rekomendowane zabezpieczenia dla wersji publicznej

#### Opcja A: CAPTCHA (zalecana)

```
Użytkownik → Upload XML → CAPTCHA → Konwersja → Pobierz XLSX
```

**Implementacja z hCaptcha (darmowe, GDPR-compliant):**

```python
# requirements.txt
httpx>=0.25.0

# config.py
HCAPTCHA_SECRET: str
HCAPTCHA_SITEKEY: str

# main.py
async def verify_captcha(token: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://hcaptcha.com/siteverify",
            data={
                "secret": settings.HCAPTCHA_SECRET,
                "response": token,
            }
        )
        return response.json().get("success", False)
```

**Limity dla wersji publicznej:**
- 3 konwersje / IP / godzina
- 10 konwersji / IP / dzień
- Max 5 MB na plik (zamiast 10)

#### Opcja B: Honeypot + rate limiting

Prostsze rozwiązanie bez zewnętrznych serwisów:

```html
<!-- Ukryte pole - boty je wypełnią -->
<input type="text" name="website" style="display:none" tabindex="-1">
```

```python
@app.post("/convert")
@limiter.limit("3/hour")
async def convert(website: str = Form(default="")):
    if website:  # Bot wypełnił honeypot
        raise HTTPException(403, "Spam detected")
    ...
```

### Porównanie wariantów

| Aspekt | Z logowaniem | Bez logowania + CAPTCHA |
|--------|--------------|-------------------------|
| Bezpieczeństwo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| UX (wygoda) | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ochrona przed botami | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Historia konwersji | ✅ | ❌ |
| Złożoność | Średnia | Niska |
| RODO | Wymaga polityki | Prostsza (mniej danych) |

### Moja rekomendacja

**Dla serwisu wewnętrznego/firmowego:** Wersja z logowaniem (obecna)

**Dla serwisu publicznego:** Wersja hybrydowa:
- Bez logowania: 3 konwersje/dzień z CAPTCHA
- Z logowaniem: 10 konwersji/dzień, historia, bez CAPTCHA

To daje elastyczność - przypadkowi użytkownicy mogą szybko skonwertować plik, a regularni użytkownicy mają dodatkowe korzyści z rejestracji.

---

## Następne kroki

1. [ ] Wdrożyć SECRET_KEY przez zmienne środowiskowe
2. [ ] Dodać .gitignore
3. [ ] Skonfigurować HTTPS na Synology
4. [ ] Dodać rate limiting (slowapi)
5. [ ] Zdecydować: logowanie vs publiczny dostęp
6. [ ] (Opcjonalnie) Dodać CAPTCHA dla wersji publicznej
7. [ ] Testy bezpieczeństwa przed produkcją

---

*Dokumentacja wygenerowana: 28.11.2025*
