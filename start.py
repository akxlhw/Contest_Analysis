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


def check_deps():
    """检查依赖是否安装"""
    try:
        import streamlit  # noqa: F401
        import openpyxl  # noqa: F401
    except ImportError:
        print("正在安装依赖...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    check_deps()
    ensure_mock_data()

    url = f"http://localhost:{PORT}"
    print(f"启动服务: {url}")

    # ============================================================
    # 通过 PYTHONPATH 注入 sitecustomize.py（Starlette 兼容性补丁）
    # sitecustomize 在 Python 启动时自动执行，比 Streamlit 任何模块都早
    # ============================================================
    project_dir = os.path.dirname(os.path.abspath(__file__))
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    if existing_pythonpath:
        new_pythonpath = f"{project_dir}{os.pathsep}{existing_pythonpath}"
    else:
        new_pythonpath = project_dir

    env = os.environ.copy()
    env["PYTHONPATH"] = new_pythonpath

    # 子进程启动 Streamlit，避免同进程 DeltaGeneratorSingleton 冲突
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
        ],
        env=env,
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
