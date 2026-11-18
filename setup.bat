@echo off
echo ============================================================
echo   PROMPTFORGE AI - ENVIRONMENT SETUP AND INSTALLATION
echo ============================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)
echo [OK] Python detected.

:: 2. Check Node.js and npm installation
npm --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)
echo [OK] Node.js and npm detected.

:: 3. Install Backend Dependencies
echo.
echo [1/4] Installing Python backend dependencies...
pip install -r backend\requirements.txt

:: 4. Check / Configure Environment File
if not exist "backend\.env" (
    echo [2/4] Initializing backend\.env from template...
    copy backend\.env.example backend\.env
) else (
    echo [2/4] backend\.env already exists.
)

:: 5. Install Frontend Dependencies & Build
echo.
echo [3/4] Installing frontend npm packages...
cd frontend
call npm install
echo Building frontend production assets...
call npm run build
cd ..

:: 6. Setup ComfyUI Directories
echo.
echo [4/4] Ensuring ComfyUI and local directories are initialized...
if not exist "comfyui\models\checkpoints" (
    mkdir "comfyui\models\checkpoints" 2>nul
)
if not exist "backend\data\storage\generations" (
    mkdir "backend\data\storage\generations" 2>nul
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo   Run 'start.bat' to launch PromptForge AI.
echo ============================================================
pause
