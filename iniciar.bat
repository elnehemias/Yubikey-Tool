@echo off
title YubiKey Eventbrite & FIDO2 Tool
cd /d "%~dp0"

:: Solicita permisos de Administrador automaticamente
net session >nul 2>&1 || (powershell -Command "Start-Process '%~f0' -Verb RunAs" & exit /b)

:: Asegura servicios de Windows y activa todas las interfaces de la YubiKey
sc config hidserv start= auto >nul 2>&1 & net start hidserv >nul 2>&1
sc config KeyIso start= auto >nul 2>&1 & net start KeyIso >nul 2>&1
ykman config usb --enable-all -f >nul 2>&1
ykman config nfc --enable-all -f >nul 2>&1

:: Abre el navegador e inicia la aplicacion web
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"
python -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
