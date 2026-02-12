@echo off
title Object Detection System - Video Processor
color 0B

echo ===================================================
echo   Object Detection System (Video Processing)
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

:: Ask for Video Path
set /p VIDEO_PATH="Enter full path to video file (or drag and drop here): "
set VIDEO_PATH=%VIDEO_PATH:"=%  rem Remove quotes if any

if not exist "%VIDEO_PATH%" (
    echo.
    echo Error: Video file not found: %VIDEO_PATH%
    echo Please try again.
    pause
    exit /b
)

echo.
echo Processing video: %VIDEO_PATH%
echo Press 'Q' inside the window to quit early.
echo.

python main.py --source "%VIDEO_PATH%" --mode video --save-output --export-data

echo.
echo Processing complete! Output files saved to 'output/'.
pause
