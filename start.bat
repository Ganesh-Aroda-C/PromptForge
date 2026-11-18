@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   PROMPTFORGE AI - LAUNCHING LOCAL SYSTEM
echo ============================================================
echo.

set "PYTHONPATH=%CD%"

:: 1. Launch ComfyUI GPU Server (Port 8188)
netstat -ano | findstr :8188 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [1/3] ComfyUI is already running on http://127.0.0.1:8188
) else (
    if exist "comfyui\main.py" (
        echo [1/3] Starting ComfyUI on http://127.0.0.1:8188 (RTX 2050 Low-VRAM FP16 Mode)...
        start "PromptForge - ComfyUI" cmd /k "set PYTHONPATH=%CD%&& python comfyui\main.py --listen 127.0.0.1 --port 8188 --lowvram --disable-auto-launch"
    ) else (
        echo [1/3] ComfyUI directory not found. Backend will operate in fallback vector/baseline mode.
    )
)

:: 2. Launch FastAPI Backend Server (Port 8000)
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [2/3] FastAPI Backend is already running on http://127.0.0.1:8000
) else (
    echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000...
    start "PromptForge - Backend" cmd /k "set PYTHONPATH=%CD%&& python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
)

:: 3. Launch React Frontend (Port 5173)
netstat -ano | findstr :5173 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [3/3] Frontend is already running on http://127.0.0.1:5173
) else (
    echo [3/3] Starting Frontend on http://127.0.0.1:5173...
    cd frontend
    start "PromptForge - Frontend" cmd /k "npm run dev -- --host 127.0.0.1 --port 5173"
    cd ..
)

:: 4. Readiness check (wait until frontend responds)
echo.
echo Waiting for services to become ready...
python -c "
import socket, time
def wait_port(port, name, max_sec=20):
    t0 = time.time()
    while time.time() - t0 < max_sec:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1.0):
                print(f'[READY] {name} is listening on port {port}.')
                return True
        except Exception:
            time.sleep(1.0)
    print(f'[WARN] {name} port {port} wait timed out (service may still be initializing).')
    return False

wait_port(8000, 'FastAPI Backend', 15)
wait_port(5173, 'React Frontend', 15)
"

echo.
echo ============================================================
echo   PROMPTFORGE AI IS LIVE!
echo   Opening: http://127.0.0.1:5173
echo ============================================================
start http://127.0.0.1:5173
