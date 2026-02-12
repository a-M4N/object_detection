@echo off
title Object Detection System - Webcam Mode
color 0B

echo ===================================================
echo   Starting Object Detection System (Webcam)
echo ===================================================
echo.

:: Check Virtual Environment
if not exist "venv" (
    echo Error: Virtual environment 'venv' not found.
    echo Please run 'install.bat' first.
    pause
    exit /b
)

:: Activate Virtual Environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Run Application
echo Starting application...
echo Press 'Q' inside the window to quit.
echo.

python main.py --source 0 --mode webcam --save-output --export-data

echo.
echo Application closed. Output files saved to 'output/'.
pause
