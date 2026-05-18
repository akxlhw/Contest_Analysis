"""一键启动：生成模拟数据 + 启动Streamlit服务 + 打开浏览器"""

import os
import subprocess
import sys
import time
import urllib.request
import webbrowser

MOCK_FILE = "mock_students.xlsx"
APP_FILE = "app.py"
PORT = 8501


def ensure_mock_data():
    """如果模拟数据不存在则生成"""
    if not os.path.exists(MOCK_FILE):
        print("模拟数据不存在，正在生成...")
        subprocess.run([sys.executable, "generate_mock_data.py"], check=True)
    else:
        print(f"模拟数据已存在: {MOCK_FILE}")


def _is_starlette_compatible():
    """检查 starlette 版本是否兼容当前 Streamlit"""
    try:
        import starlette

        major = int(starlette.__version__.split(".")[0])
        return major < 1
    except Exception:
        return False


def check_deps():
    """检查依赖是否安装且版本兼容"""
    need_install = False
    try:
        import streamlit  # noqa: F401
        import openpyxl  # noqa: F401
    except ImportError:
        need_install = True

    if not _is_starlette_compatible():
        print("[WARN] Starlette 版本不兼容，需要降级到 <1.0.0...")
        need_install = True

    if need_install:
        print("正在安装/修复依赖...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "starlette<1.0.0", "-r", "requirements.txt"],
            check=True,
        )


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    check_deps()
    ensure_mock_data()

    url = f"http://localhost:{PORT}"
    print(f"启动服务: {url}")

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            APP_FILE,
            "--server.port",
            str(PORT),
            "--browser.gatherUsageStats",
            "false",
            "--server.headless",
            "true",
        ]
    )

    # 等待服务就绪后打开浏览器
    for _ in range(30):
        try:
            urllib.request.urlopen(url, timeout=2)
            break
        except Exception:
            time.sleep(1)

    webbrowser.open(url)
    print(f"浏览器已打开: {url}")
    print("按 Ctrl+C 停止服务")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
