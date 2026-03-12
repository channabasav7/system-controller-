@echo off
echo ================================================================
echo   TOUCHLESS LAPTOP CONTROL SYSTEM - Setup Script
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python detected
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping.
) else (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [5/5] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] Some packages may have failed to install.
    echo If PyAudio failed, you may need to install it manually:
    echo 1. Download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo 2. Run: pip install PyAudio-0.2.14-cpXXX-cpXXX-win_amd64.whl
    echo.
    pause
) else (
    echo.
    echo ================================================================
    echo   SETUP COMPLETE!
    echo ================================================================
    echo.
    echo To run the application:
    echo   1. Activate virtual environment: venv\Scripts\activate
    echo   2. Run: python main.py
    echo.
    echo Or simply run: run.bat
    echo.
)

pause
