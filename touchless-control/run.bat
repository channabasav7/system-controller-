@echo off
echo ================================================================
echo   TOUCHLESS LAPTOP CONTROL SYSTEM - Starting...
echo ================================================================
echo.

REM Check if virtual environment exists (supports both names)
set VENV_PATH=
if exist venv\Scripts\activate.bat set VENV_PATH=venv
if exist ..\.venv-1\Scripts\activate.bat set VENV_PATH=..\.venv-1

if "%VENV_PATH%"=="" (
    echo [ERROR] Virtual environment not found.
    echo Expected one of:
    echo   - touchless-control\venv
    echo   - .venv-1 in project root
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call %VENV_PATH%\Scripts\activate.bat

REM Preflight: show runtime versions (Python/OpenCV/MediaPipe/Tkinter)
echo [INFO] Runtime dependency check...
python -c "import sys, cv2, mediapipe as mp, tkinter as tk; print('[INFO] Python   :', sys.version.split()[0]); print('[INFO] OpenCV   :', cv2.__version__); print('[INFO] MediaPipe:', mp.__version__); print('[INFO] Tkinter  :', tk.TkVersion)"
if errorlevel 1 (
    echo [ERROR] Dependency check failed. Ensure OpenCV, MediaPipe, and Tkinter are installed.
    pause
    exit /b 1
)
echo.

REM Run the application
python main.py

REM Deactivate when done
deactivate
