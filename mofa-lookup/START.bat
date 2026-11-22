@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt || exit /b 1
python -m playwright install chromium || exit /b 1
start http://127.0.0.1:8765
python app.py
pause
