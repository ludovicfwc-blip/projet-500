@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
"%~dp0venv\Scripts\python.exe" "%~dp0run_all.py" >> "%~dp0logs\scraper.log" 2>&1
