@echo off
title Daniel's Donuts - Install Dependencies
cd /d "%~dp0"

echo ========================================
echo  Installing Python dependencies...
echo ========================================
echo.
"C:\Users\natan.akoka1\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m pip install -r requirements.txt

echo.
echo ========================================
echo  Installing Node dependencies...
echo ========================================
echo.
cd dashboard
npm install

echo.
echo Done! You can now run start_backend.bat and start_dashboard.bat
pause
