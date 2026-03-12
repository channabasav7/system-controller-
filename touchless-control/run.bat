@echo off
echo ================================================================
echo   TOUCHLESS LAPTOP CONTROL SYSTEM - Starting...
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python main.py

REM Deactivate when done
deactivate
