@echo off
title Daniel's Donuts - Dashboard
echo Starting Daniel's Donuts Dashboard on http://localhost:5173
echo.
cd /d "%~dp0\dashboard"
npm run dev
pause
