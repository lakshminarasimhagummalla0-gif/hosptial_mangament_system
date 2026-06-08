@echo off
title CareSync - Hospital Management System
color 0B

echo.
echo  ============================================================
echo   Starting CareSync Hospital Management System...
echo  ============================================================
echo.
echo  The app will open in your browser automatically.
echo  Press Ctrl+C in this window to stop the server.
echo.

cd /d "%~dp0"

REM Open browser after 2 seconds
start "" timeout /t 2 >nul
start "" cmd /c "timeout /t 2 >nul && start http://127.0.0.1:5000"

REM Start Flask app
"%~dp0.venv\Scripts\python.exe" app.py

echo.
echo  Server stopped.
pause
