@echo off
title CareSync - Auto Deployer
color 0A

echo.
echo  ============================================================
echo   CARESYNC HOSPITAL - AUTO DEPLOYMENT LAUNCHER
echo  ============================================================
echo.
echo  Choose what you want to do:
echo.
echo  [1] Deploy to Internet (GitHub + Render.com) - FREE
echo  [2] Share on Local WiFi Network RIGHT NOW
echo  [3] Open app in browser (localhost)
echo  [4] Exit
echo.
set /p choice="  Enter choice (1/2/3/4): "

if "%choice%"=="1" goto deploy_internet
if "%choice%"=="2" goto local_network
if "%choice%"=="3" goto open_browser
if "%choice%"=="4" goto end

:deploy_internet
echo.
echo  Starting automated deployment to internet...
echo  (This will walk you through each step automatically)
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0auto_deploy.ps1"
goto end

:local_network
echo.
echo  Starting CareSync on your local WiFi network...
echo  Other devices can access it using the URL shown below.
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0run_local_network.py"
goto end

:open_browser
echo.
echo  Opening CareSync in your browser...
start http://127.0.0.1:5000
echo  Done! If the page doesn't load, make sure app.py is running.
echo.
pause
goto end

:end
echo.
echo  Goodbye!
timeout /t 2 >nul
