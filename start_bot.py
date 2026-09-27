"""
網站護理智慧助手 — 一鍵啟動與 Tunnel 工具
==========================================
自動啟動 Flask Web 伺服器 (app.py) 並建立 Cloudflare 安全穿透 Tunnel (cloudflared.exe)。
"""

import sys
import time
import subprocess
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(msg):
    print(msg, flush=True)

def main():
    log("=" * 60)
    log("🚀 正在啟動 網站護理智慧助手 (Port 5000)...")
    log("=" * 60)

    # 1. 啟動 app.py
    app_proc = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    time.sleep(2)

    # 2. 啟動 cloudflared
    log("🌐 正在建立 Cloudflare 網頁公網穿透 Tunnel...")
    tunnel_proc = subprocess.Popen(
        [".\\cloudflared.exe", "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    public_url = None
    start_time = time.time()

    # 3. 解析 Cloudflare Tunnel 產生的 URL
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            break

    log("\n" + "★" * 60)
    log(" 🎉 網站護理智慧助手 啟動成功！")
    log("★" * 60)
    log(f"\n💻 本地電腦存取網址：  http://localhost:5000")
    if public_url:
        log(f"🌐 任何裝置公網網址：  {public_url}")
        log(f"📱 LINE Webhook 網址： {public_url}/callback")
    log("\n" + "=" * 60)
    log("按 Ctrl+C 可停止網站與 Tunnel 服務。")
    log("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\n🛑 正在停止 網站護理智慧助手 伺服器與 Tunnel...")
        tunnel_proc.terminate()
        app_proc.terminate()
        log("完成。")

if __name__ == "__main__":
    main()
