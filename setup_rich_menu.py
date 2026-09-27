"""
LINE Bot 四格圖文選單 (Rich Menu) 自動建立與設定腳本
=====================================================
建立含「護理」、「藥物」、「疾病」、「衛教」4格功能選單：
- Top-Left     (0, 0, 1250, 843)     : 🩺 護理
- Top-Right    (1250, 0, 1250, 843)  : 💊 藥物
- Bottom-Left  (0, 843, 1250, 843)   : 📋 疾病
- Bottom-Right (1250, 843, 1250, 843): 📄 衛教
"""

import os
import io
import json
import logging
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RichMenuSetup")

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_ACCESS_TOKEN.startswith("YOUR_"):
    raise ValueError("請先在 .env 設定有效的 LINE_CHANNEL_ACCESS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def create_rich_menu_image() -> bytes:
    """使用 Pillow 動態繪製 2500 x 1686 像素的 4 格圖文選單圖片"""
    width, height = 2500, 1686
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)

    # 格子配置
    cards = [
        # (x1, y1, x2, y2, bg_color, title, subtitle, icon)
        (30, 30, 1220, 813, "#00B894", "🩺 護理", "護理技術與步驟查詢", "#FFFFFF"),
        (1280, 30, 2470, 813, "#6C5CE7", "💊 藥物", "藥物資訊與學名查詢", "#FFFFFF"),
        (30, 873, 1220, 1656, "#E17055", "📋 疾病", "臨床疾病照護指引", "#FFFFFF"),
        (1280, 873, 2470, 1656, "#0984E3", "📄 衛教", "病人衛教單張與說明", "#FFFFFF"),
    ]

    # 嘗試載入微軟正黑體或預設字型
    font_title = None
    font_sub = None
    font_paths = [
        "C:\\Windows\\Fonts\\msjhbd.ttc",  # 微軟正黑體 粗體
        "C:\\Windows\\Fonts\\msjh.ttc",    # 微軟正黑體
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_title = ImageFont.truetype(font_path, 110)
                font_sub = ImageFont.truetype(font_path, 52)
                logger.info(f"成功載入字型: {font_path}")
                break
            except Exception:
                continue

    if font_title is None:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    for x1, y1, x2, y2, bg_color, title, subtitle, text_color in cards:
        # 繪製圓角卡片
        draw.rounded_rectangle([x1, y1, x2, y2], radius=40, fill=bg_color)

        # 計算文字位置 (垂直居中)
        box_center_x = (x1 + x2) // 2
        box_center_y = (y1 + y2) // 2

        # 標題
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        draw.text(
            (box_center_x - title_w // 2, box_center_y - title_h - 20),
            title,
            fill=text_color,
            font=font_title,
        )

        # 副標題
        sub_bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        sub_w = sub_bbox[2] - sub_bbox[0]
        draw.text(
            (box_center_x - sub_w // 2, box_center_y + 30),
            subtitle,
            fill="#EAEAEA",
            font=font_sub,
        )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def setup_rich_menu():
    """建立並設定預設 Rich Menu"""
    logger.info("1️⃣ 建立 4 格 Rich Menu 結構...")
    rich_menu_object = {
        "size": {"width": 2500, "height": 1686},
        "selected": True,
        "name": "NurseBot_4Grid_Menu",
        "chatBarText": "🏥 護理智慧查詢選單",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "護理"},
            },
            {
                "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "藥物"},
            },
            {
                "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "疾病"},
            },
            {
                "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "衛教"},
            },
        ],
    }

    # 1. 建立 Rich Menu
    resp = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=HEADERS,
        json=rich_menu_object,
    )
    resp.raise_for_status()
    rich_menu_id = resp.json()["richMenuId"]
    logger.info(f"✅ Rich Menu 建立成功，ID: {rich_menu_id}")

    # 2. 上傳圖文選單圖片
    logger.info("2️⃣ 生成並上傳圖文選單圖片 (2500x1686)...")
    img_bytes = create_rich_menu_image()
    img_headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "image/png",
    }
    upload_url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"
    resp_img = requests.post(upload_url, headers=img_headers, data=img_bytes)
    resp_img.raise_for_status()
    logger.info("✅ 圖片上傳成功！")

    # 3. 設為所有人預設選單
    logger.info("3️⃣ 設定為預設圖文選單...")
    default_url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
    resp_def = requests.post(default_url, headers=HEADERS)
    resp_def.raise_for_status()
    logger.info("🎉 預設圖文選單設定成功！所有人開啟 LINE 即可看到「護理」、「藥物」、「疾病」、「衛教」四格選單！")


if __name__ == "__main__":
    setup_rich_menu()
