@echo off
rem ===================================================================
rem  Konwerter Sprawozdan Finansowych - tryb "przeciagnij i upusc".
rem
rem  Uzycie: przeciagnij pliki XML / XAdES na ikone tego pliku.
rem  Sprawozdania tego samego podmiotu (ten sam NIP/KRS) zostana
rem  polaczone w jeden plik Excel z kolumnami kolejnych lat.
rem ===================================================================
chcp 65001 >nul
title Konwerter Sprawozdan Finansowych

set "PYEXE=python"
where python >nul 2>nul || set "PYEXE=py"

"%PYEXE%" "%~dp0src\konwertuj.py" %*

echo.
echo Nacisnij dowolny klawisz, aby zamknac to okno...
pause >nul
