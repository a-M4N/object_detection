@echo off
title Object Detection System - Installer
color 0A

echo ===================================================
echo   Real-Time Object Detection System Installer
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b
)

:: Create Virtual Environment
if not exist "venv" (
    echo [1/4] Creating virtual environment 'venv'...
    python -m venv venv
) else (
    echo [1/4] Virtual environment already exists.
)

:: Activate Virtual Environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate

:: Upgrade pip
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

:: Install Dependencies
echo [4/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ===================================================
echo   Installation Complete!
echo ===================================================
echo.
echo Running installation test...
echo.

python test_installation.py

echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] System is ready to use!
) else (
    echo [WARNING] Some tests failed. Please checks logs above.
)

echo.
pause
