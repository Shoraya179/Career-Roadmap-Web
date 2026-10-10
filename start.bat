@echo off
echo ========================================================
echo       Starting CareerForge AI (Backend + Frontend)
echo ========================================================
echo.

:: Ensure portable node and python are in PATH for this session
set "PATH=%PATH%;C:\Users\anami\AppData\Local\Programs\nodejs;C:\Users\anami\AppData\Local\Programs\Python\Python314"

echo [1/2] Starting Backend API Server (http://127.0.0.1:8000)...
start "CareerForge Backend" cmd /k "py backend/app.py"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Frontend Vite App (http://localhost:5173)...
start "CareerForge Frontend" cmd /k "npm.cmd run dev"

echo.
echo ========================================================
echo Both servers launched! Opening browser...
echo ========================================================
timeout /t 2 /nobreak >nul
start http://localhost:5173
