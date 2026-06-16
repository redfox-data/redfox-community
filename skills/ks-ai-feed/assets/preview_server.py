#!/usr/bin/env python3
"""启动带图片代理的本地预览服务，根路径自动重定向到最新快手日报"""
import sys
import os

# 将 daily_report 的目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daily_report import ProxyHTTPHandler, info
from pathlib import Path
from http.server import HTTPServer

output_dir = Path.home() / "Downloads" / "QoderReports"

# 动态找最新生成的快手日报文件
html_files = sorted(output_dir.glob("AI快手日报_*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
latest = html_files[0].name if html_files else None


class RedirectHandler(ProxyHTTPHandler):
    """在 ProxyHTTPHandler 基础上，根路径自动重定向到最新快手日报"""
    latest_file = latest

    def do_GET(self):
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        if parsed.path in ("/", "") and self.latest_file:
            self.send_response(302)
            self.send_header("Location", f"/{self.latest_file}")
            self.end_headers()
        else:
            super().do_GET()


os.chdir(str(output_dir))
server = HTTPServer(("127.0.0.1", 8766), RedirectHandler)

import threading
t = threading.Thread(target=server.serve_forever, daemon=False)
t.start()

info(f"本地服务已启动: http://127.0.0.1:8766")
if latest:
    print(f"\n预览地址: http://127.0.0.1:8766/{latest}")
else:
    print("\n未找到快手日报文件")
print("按 Ctrl+C 退出\n")

try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n服务已停止")
