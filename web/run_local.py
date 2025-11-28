#!/usr/bin/env python
"""
Skrypt do lokalnego uruchamiania aplikacji.

Użycie:
    python run_local.py

Lub bezpośrednio uvicorn:
    uvicorn app.main:app --reload --port 8000
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("Konwerter SF - serwer deweloperski")
    print("=" * 50)
    print("Aplikacja będzie dostępna pod adresem:")
    print("  http://localhost:8000")
    print("")
    print("Dokumentacja API (Swagger):")
    print("  http://localhost:8000/docs")
    print("")
    print("Naciśnij Ctrl+C aby zatrzymać serwer")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],
    )
