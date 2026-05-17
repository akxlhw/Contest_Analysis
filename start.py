"""一键启动：生成模拟数据 + 启动Streamlit服务 + 打开浏览器"""

import os
import sys
import webbrowser
import subprocess

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


def check_deps():
    """检查依赖是否安装"""
    try:
        import streamlit  # noqa: F401
        import openpyxl  # noqa: F401
    except ImportError:
        print("正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    check_deps()
    ensure_mock_data()

    url = f"http://localhost:{PORT}"
    print(f"启动服务: {url}")

    # 后台启动Streamlit
    proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", APP_FILE,
        "--server.port", str(PORT),
        "--browser.gatherUsageStats", "false",
        "--server.headless", "true",
    ])

    # 等待服务就绪后打开浏览器
    import time
    for _ in range(30):
        try:
            import urllib.request
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
