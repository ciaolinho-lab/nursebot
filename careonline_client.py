"""
CareOnline 照護線上 衛教資料庫查詢客戶端
=========================================
從 照護線上 (https://www.careonline.com.tw/?utm_source=gemini) 搜尋衛教文章與單張。
"""

import logging
import re
import urllib.parse
import html as html_lib
import requests

logger = logging.getLogger(__name__)

CAREONLINE_BASE_URL = "https://www.careonline.com.tw/"

class CareOnlineClient:
    """照護線上衛教資料庫 API / Web Scraper"""

    def __init__(self, timeout: int = 2.5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        })

    def search_education(self, keyword: str) -> list:
        """根據關鍵字搜尋照護線上衛教文章"""
        if not keyword or not keyword.strip():
            return []

        keyword = keyword.strip()
        encoded_kw = urllib.parse.quote(keyword)
        search_url = f"{CAREONLINE_BASE_URL}?s={encoded_kw}"

        try:
            logger.info(f"🌐 向 照護線上 查詢衛教單張: {keyword}")
            resp = self.session.get(search_url, timeout=self.timeout)
            resp.encoding = "utf-8"
            if resp.status_code != 200:
                logger.warning(f"CareOnline HTTP {resp.status_code}")
                return []

            return self._parse_search_results(resp.text)

        except Exception as e:
            logger.error(f"CareOnline 查詢發生例外: {e}")
            return []

    def _parse_search_results(self, html: str) -> list:
        """解析搜尋結果頁面 HTML"""
        articles = re.findall(r'<article\s+id="post-\d+"[^>]*>(.*?)</article>', html, re.DOTALL)
        results = []

        for art in articles:
            # 1. 標題與連結
            title_match = re.search(
                r'<h2[^>]*class="[^"]*post-title[^"]*"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>\s*</h2>',
                art,
                re.DOTALL
            )
            if not title_match:
                title_match = re.search(
                    r'<a[^>]*href="(https://www\.careonline\.com\.tw/[^"]+)"[^>]*title="([^"]+)"',
                    art
                )

            if not title_match:
                continue

            url = title_match.group(1).strip()
            raw_title = title_match.group(2)
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            title = html_lib.unescape(title)

            if not title or not url:
                continue

            # 2. 縮圖 URL
            img_match = re.search(r'<img[^>]+src="([^"]+)"', art)
            image_url = img_match.group(1) if img_match else ""

            # 3. 內文摘要
            excerpt_match = re.search(r'<div[^>]*class="[^"]*excerpt[^"]*"[^>]*>(.*?)</div>', art, re.DOTALL)
            snippet = ""
            if excerpt_match:
                raw_snippet = excerpt_match.group(1)
                # 移除 Read More 按鈕
                raw_snippet = re.sub(r'<a[^>]*class="read-more-button"[^>]*>.*?</a>', '', raw_snippet, flags=re.DOTALL)
                snippet = re.sub(r'<[^>]+>', '', raw_snippet).strip()
                snippet = html_lib.unescape(snippet)

            # 加上 utm_source=gemini
            clean_url = url.split('#')[0]
            if "utm_source=" not in clean_url:
                connector = "&" if "?" in clean_url else "?"
                clean_url = f"{clean_url}{connector}utm_source=gemini"

            # 避免重複 URL
            if not any(r['url'] == clean_url for r in results):
                results.append({
                    "title": title,
                    "url": clean_url,
                    "image_url": image_url,
                    "snippet": snippet,
                    "summary": snippet,
                    "category": "衛教單張",
                    "source": "照護線上 CareOnline",
                })

        return results
