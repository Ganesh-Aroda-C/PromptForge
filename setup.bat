@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   PROMPTFORGE AI - ENVIRONMENT AUDIT AND SETUP
echo ============================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo [OK] Python detected: %%v

:: 2. Check PyTorch and CUDA acceleration
python -c "import torch; print(f'[OK] PyTorch version: {torch.__version__} | CUDA available: {torch.cuda.is_available()} | Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

:: 3. Check Node.js and npm
npm --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('npm --version') do echo [OK] npm detected: v%%v

:: 4. Check Backend Dependencies (Reuse existing environment)
echo.
python -c "import fastapi, uvicorn, pydantic, PIL, motor, pymongo, requests" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python backend dependencies are already installed. Skipping pip install.
) else (
    echo [1/4] Installing missing Python backend dependencies...
    pip install -r backend\requirements.txt
)

:: 5. Check Environment File
if not exist "backend\.env" (
    echo [2/4] Initializing backend\.env from template...
    copy backend\.env.example backend\.env
) else (
    echo [OK] backend\.env already exists.
)

:: 6. Check Frontend Dependencies & Build (Reuse existing node_modules)
echo.
if exist "frontend\node_modules" (
    echo [OK] Frontend node_modules already installed.
) else (
    echo [3/4] Installing frontend dependencies...
    cd frontend && call npm install && cd ..
)

if not exist "frontend\dist\index.html" (
    echo Building frontend production assets...
    cd frontend && call npm run build && cd ..
) else (
    echo [OK] Frontend production bundle already built.
)

:: 7. Check ComfyUI Model Weights
echo.
echo [4/4] Verifying local model checkpoints...
if exist "comfyui\models\checkpoints\v1-5-pruned-emaonly.safetensors" (
    echo [OK] Stable Diffusion 1.5 weights detected: comfyui\models\checkpoints\v1-5-pruned-emaonly.safetensors
) else (
    echo [NOTE] SD 1.5 weights not found in standard path. Please ensure checkpoint is placed in comfyui\models\checkpoints\
)

if not exist "backend\data\storage\generations" (
    mkdir "backend\data\storage\generations" 2>nul
)

echo.
echo ============================================================
echo   SETUP VERIFICATION COMPLETE!
echo   Run 'start.bat' to launch PromptForge AI.
echo ============================================================
pause
