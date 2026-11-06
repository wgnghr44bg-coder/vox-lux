@echo off
rem Audio Engine starten: opent http://127.0.0.1:7865 in de browser.
cd /d "%~dp0"
"C:\Users\rane\omnivoice-venv\Scripts\python.exe" main.py ui
pause
