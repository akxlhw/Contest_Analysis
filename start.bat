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

:: 检查 Starlette 版本，不兼容则强制降级
python -c "import starlette; import sys; sys.exit(0 if int(starlette.__version__.split('.')[0]) < 1 else 1)" >nul 2>&1
if %errorlevel% neq 0 goto downgrade_starlette
goto starlette_ok

:downgrade_starlette
echo [WARN] Starlette 版本不兼容，正在降级...
python -m pip install --upgrade --force-reinstall "starlette<1.0.0" -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Starlette 降级失败，请检查 pip 是否能正常访问安装源
    pause
    exit /b 1
)
echo [OK] Starlette 已降级到兼容版本

:starlette_ok

:: 检查其他核心依赖
python -c "import streamlit, openpyxl" >nul 2>&1
if %errorlevel% equ 0 goto deps_ok

echo 正在安装其他依赖...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] 依赖安装失败
    pause
    exit /b 1
)

:deps_ok
if not exist "mock_students.xlsx" (
    echo 正在生成模拟数据...
    python generate_mock_data.py
) else (
    echo 模拟数据已存在: mock_students.xlsx
)

echo.
echo 正在启动服务...
echo URL: http://localhost:8501
echo 按 Ctrl+C 停止
echo.

start http://localhost:8501
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false --server.headless true

pause
