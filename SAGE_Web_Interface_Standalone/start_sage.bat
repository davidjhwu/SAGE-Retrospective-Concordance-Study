@echo off
echo ========================================
echo   SAGE Medical AI Review Tool
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Starting SAGE Web Interface...
echo.
echo ========================================
echo   Access the tool at:
echo   http://localhost:5001
echo   Password: djhwu
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause