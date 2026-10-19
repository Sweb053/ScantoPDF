@echo off
title Marker Scan to Markdown
cd /d "C:\Users\seanw\Documents\ChatGPT\Book to .md File Converter"

python -c "import streamlit, marker" >nul 2>&1
if errorlevel 1 (
    echo Marker is not installed yet.
    echo Installing Marker and its dependencies may take several minutes...
    python -m pip install -r requirements-marker.txt
    if errorlevel 1 (
        echo.
        echo Installation failed. Check your internet connection and available disk space.
        pause
        exit /b 1
    )
)

echo Starting the Marker scan converter...
echo The first conversion downloads large model files and may take some time.
echo Keep this window open while using the application.
echo.
python -m streamlit run marker_scan_app.py

if errorlevel 1 (
    echo.
    echo The application could not start. Review the message above for details.
    pause
)
