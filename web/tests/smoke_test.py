"""Smoke test aplikacji webowej w tymczasowym kontenerze (bez dotykania produkcji).

Uruchamiany z /app w kontenerze z obrazu web-web:latest, z env:
DATABASE_URL=sqlite+aiosqlite:////tmp/smoke.db, RECAPTCHA_ENABLED=false, SECRET_KEY=smoke.
"""
import asyncio, io, os, sys, glob, sqlite3
sys.path.insert(0, '/app')
from fastapi.testclient import TestClient
import openpyxl
from app.main import app
from app.database import async_session, init_db
from app.models import User
from app.auth import get_password_hash, verify_password

ok = True
def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('OK   ' if cond else 'FAIL ') + name + (('  ' + extra) if extra else ''))

async def mk_admin():
    await init_db()
    async with async_session() as db:
        db.add(User(email='smoke@test.local', hashed_password=get_password_hash('Haslo-Smoke-123'),
                    is_admin=True, is_active=True))
        await db.commit()

with TestClient(app) as c:
    r = c.get('/'); check('GET / 200', r.status_code == 200)
    for p in ('/regulamin', '/polityka-prywatnosci', '/admin/login'):
        r = c.get(p); check(f'GET {p} 200', r.status_code == 200)

    # konwersja kazdego XML z /tmp/smoke/*.xml
    for f in sorted(glob.glob('/tmp/smoke/*.xml')):
        name = os.path.basename(f)
        r = c.post('/htmx/convert', files={'file': (name, open(f, 'rb').read(), 'application/xml')})
        body = r.text
        import re
        m = re.search(r'/download/([0-9a-f\-]{36})"', body)
        check(f'POST /htmx/convert {name}: status 200 i link', r.status_code == 200 and m is not None,
              '' if m else body[body.find('error'):body.find('error') + 300].replace('\n', ' '))
        if m:
            d = c.get('/download/' + m.group(1))
            ok_x = d.status_code == 200 and d.content[:2] == b'PK'
            sheets = []
            if ok_x:
                wb = openpyxl.load_workbook(io.BytesIO(d.content))
                sheets = wb.sheetnames
            check(f'GET /download {name}: XLSX', ok_x and len(sheets) > 0, ', '.join(sheets))

    # plik niepoprawny -> czytelny blad, nie 500
    r = c.post('/htmx/convert', files={'file': ('zly.xml', b'<a>nie sprawozdanie</a>', 'application/xml')})
    check('POST /htmx/convert zly XML: 200 z komunikatem', r.status_code == 200 and 'error' in r.text.lower())

    # logowanie admina (bcrypt 5.0)
    asyncio.get_event_loop().run_until_complete(mk_admin()) if False else asyncio.run(mk_admin())
    r = c.post('/admin/login', data={'email': 'smoke@test.local', 'password': 'zle-haslo'}, follow_redirects=False)
    check('POST /admin/login zle haslo: 401', r.status_code == 401)
    r = c.post('/admin/login', data={'email': 'smoke@test.local', 'password': 'Haslo-Smoke-123'}, follow_redirects=False)
    check('POST /admin/login dobre haslo: 302 + cookie', r.status_code == 302 and 'access_token' in r.cookies)
    r = c.get('/admin')
    check('GET /admin po zalogowaniu: 200', r.status_code == 200)

# zgodnosc bcrypt 5 z hashami z produkcyjnej bazy (tylko odczyt kopii, bez hasel)
prod = '/prod/app.db'
if os.path.exists(prod):
    con = sqlite3.connect(f'file:{prod}?mode=ro', uri=True)
    rows = con.execute('select hashed_password from users').fetchall()
    for (h,) in rows:
        try:
            res = verify_password('to-nie-jest-haslo', h)
            check(f'bcrypt 5 czyta hash produkcyjny ({h[:4]}...)', res is False)
        except Exception as e:
            check('bcrypt 5 czyta hash produkcyjny', False, repr(e))
    con.close()
else:
    print('INFO brak /prod/app.db - test hashy produkcyjnych pominiety')

print('WYNIK:', 'WSZYSTKO OK' if ok else 'SA BLEDY')
