@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1
python -m pip install pyinstaller
if errorlevel 1 pause & exit /b 1
python -m PyInstaller --noconfirm --clean --onefile --windowed --name UndeadStreets game.py
if errorlevel 1 (
  echo Build failed. See the error above.
  pause
  exit /b 1
)
echo.
echo Build complete: dist\UndeadStreets.exe
pause
