@echo off
echo ============================================================
echo   PROMPTFORGE AI - STARTING SERVICES
echo ============================================================
echo.

:: 1. Start Local ComfyUI Server if installed
if exist "comfyui\main.py" (
    echo [1/3] Starting ComfyUI on http://127.0.0.1:8188 - Low VRAM Mode for RTX 2050
    start "PromptForge - ComfyUI" cmd /k "python comfyui\main.py --listen 127.0.0.1 --port 8188 --lowvram --disable-auto-launch"
) else (
    echo [1/3] ComfyUI local server not found. Backend will use free dynamic synthesizer fallback.
)

:: 2. Start FastAPI Backend Server
echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000
start "PromptForge - Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait 2 seconds for backend initialization
ping 127.0.0.1 -n 3 >nul

:: 3. Start Frontend Development Server
echo [3/3] Starting Frontend on http://127.0.0.1:5173
cd frontend
start "PromptForge - Frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
cd ..

:: Wait 3 seconds then open browser
ping 127.0.0.1 -n 4 >nul
echo.
echo ============================================================
echo   PROMPTFORGE AI IS LIVE!
echo   Opening: http://127.0.0.1:5173
echo ============================================================
start http://127.0.0.1:5173
