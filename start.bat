@echo off
title 智能高考志愿填报系统 - Sharing Server
echo ============================================
echo   智能高考志愿填报系统
echo ============================================
echo.

REM Start backend (FastAPI)
echo [1/3] Starting backend API...
start "Gaokao-Backend" cmd /c "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start frontend (Vite dev with proxy)
echo [2/3] Starting frontend...
start "Gaokao-Frontend" cmd /c "cd frontend && npm run dev -- --host 0.0.0.0"

REM Wait for frontend
timeout /t 3 /nobreak >nul

REM Start localtunnel
echo [3/3] Starting public tunnel...
echo.
echo ============================================
echo   Share this URL:
echo.
lt --port 5173 2>&1 | findstr "your url is:"
echo.
echo   Open the URL and click "Click to Continue"
echo   The system is ready to use!
echo ============================================
echo.
echo Press Ctrl+C to stop all services.

REM Keep the tunnel alive
:loop
lt --port 5173
timeout /t 3 /nobreak >nul
goto loop
