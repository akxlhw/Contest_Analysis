"""Starlette 兼容性补丁：在 Python 启动时自动注入

新版 Starlette 移除了 DEFAULT_EXCLUDED_CONTENT_TYPES 常量，
旧版 Streamlit 导入 starlette_gzip_middleware 时会因此崩溃。

通过 PYTHONPATH 将此文件注入子进程，即可在 Streamlit 任何模块导入之前完成 patch，
无需降级 Starlette，也无需修改 site-packages 中的 Streamlit 源码。
"""

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
