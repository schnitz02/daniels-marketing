@echo off
title Daniel's Donuts - Backend API
cd /d "%~dp0"

echo ========================================
echo  Daniel's Donuts - Backend Startup
echo ========================================
echo.
echo Working directory: %CD%
echo.

echo [1/3] Checking Python...
"C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe" --version
if errorlevel 1 (
    echo ERROR: Python not found at expected path!
    pause
    exit /b 1
)

echo.
echo [2/3] Checking key packages...
"C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe" -c "import fastapi, uvicorn, sqlalchemy, anthropic, apscheduler, dotenv; print('All packages OK')"
if errorlevel 1 (
    echo ERROR: Missing Python packages. Run install_deps.bat first.
    pause
    exit /b 1
)

echo.
echo [3/3] Starting backend on http://localhost:8000 ...
echo.
"C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m src.main

echo.
echo Backend stopped.
pause
