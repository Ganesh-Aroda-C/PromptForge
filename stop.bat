@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   PROMPTFORGE AI - SAFE SHUTDOWN
echo ============================================================
echo.

echo Terminating PromptForge services on ports 8188 (ComfyUI), 8000 (Backend), and 5173 (Frontend)...

:: Terminate Port 8188 (ComfyUI)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8188 ^| findstr LISTENING 2^>nul') do (
    echo Stopping ComfyUI process (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)

:: Terminate Port 8000 (FastAPI Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo Stopping Backend process (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)

:: Terminate Port 5173 (React Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING 2^>nul') do (
    echo Stopping Frontend process (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)

echo.
echo ============================================================
echo   PROMPTFORGE AI SERVICES SAFELY TERMINATED.
echo ============================================================
pause
