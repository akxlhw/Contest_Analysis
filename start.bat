@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ================================
echo   ICPC Label Tool
echo ================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

python start.py

pause
