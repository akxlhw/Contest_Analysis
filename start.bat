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

python -c "import streamlit, openpyxl" >nul 2>&1
if %errorlevel% equ 0 goto deps_ok

echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

:deps_ok
if not exist "mock_students.xlsx" (
    echo Generating mock data...
    python generate_mock_data.py
) else (
    echo Mock data exists: mock_students.xlsx
)

echo.
echo Starting server...
echo URL: http://localhost:8501
echo Press Ctrl+C to stop
echo.

start http://localhost:8501
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false --server.headless true

pause
