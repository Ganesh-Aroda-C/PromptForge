@echo off
echo ============================================================
echo   PROMPTFORGE AI - STOPPING ALL SERVICES
echo ============================================================
echo.

echo Stopping Uvicorn / FastAPI processes...
taskkill /F /IM python.exe /T 2>nul

echo Stopping Node.js / Vite processes...
taskkill /F /IM node.exe /T 2>nul

echo.
echo All PromptForge AI processes stopped safely.
echo ============================================================
pause
