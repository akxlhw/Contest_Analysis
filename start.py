"""一键启动：生成模拟数据 + 启动Streamlit服务 + 打开浏览器"""

# ============================================================
# Starlette 兼容性补丁（必须在导入 Streamlit 之前执行）
# ============================================================
# 新版 Starlette 移除了/改变了 DEFAULT_EXCLUDED_CONTENT_TYPES 常量，
# 旧版 Streamlit 在导入 starlette_gzip_middleware 时会因此崩溃。
# 在导入 Streamlit 任何模块之前，手动补回该常量即可避免降级 Starlette。
try:
    import starlette.middleware.gzip

    if not hasattr(starlette.middleware.gzip, "DEFAULT_EXCLUDED_CONTENT_TYPES"):
        starlette.middleware.gzip.DEFAULT_EXCLUDED_CONTENT_TYPES = (
            "image/",
            "video/",
            "audio/",
            "application/gzip",
            "application/zip",
            "application/x-tar",
        )
except Exception:
    pass

import os
import sys
import threading
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
        import subprocess

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
        import subprocess

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )


def _wait_for_server(url: str, timeout: int = 30) -> bool:
    """轮询等待服务就绪"""
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    check_deps()
    ensure_mock_data()

    url = f"http://localhost:{PORT}"
    print(f"启动服务: {url}")
    print("按 Ctrl+C 停止服务")

    # 在后台线程等待服务就绪后打开浏览器
    def _open_browser():
        if _wait_for_server(url):
            webbrowser.open(url)
            print(f"浏览器已打开: {url}")

    threading.Thread(target=_open_browser, daemon=True).start()

    # 直接在当前进程内启动 Streamlit，patch 已生效
    import streamlit.web.cli as cli

    cli.main(
        args=[
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


if __name__ == "__main__":
    main()
