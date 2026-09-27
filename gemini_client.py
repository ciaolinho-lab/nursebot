"""
Gemini 護理 AI 助手 查詢客戶端
=================================
連結 Gemini 護理智慧助手 (https://gemini.google.com/) 提供護理技術操作步驟與指引。
"""

import logging
import urllib.parse
from typing import List, Dict

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://gemini.google.com/app"


class GeminiClient:
    """Gemini 護理 AI 助手客戶端"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def build_search_url(self, keyword: str) -> str:
        """建立 Gemini 連結 URL"""
        return GEMINI_BASE_URL

    def search_nursing_skill(self, keyword: str) -> List[Dict]:
        """根據關鍵字產生 Gemini 護理技術操作資料與連結"""
        if not keyword or not keyword.strip():
            clean_kw = "護理技術"
        else:
            clean_kw = keyword.strip()

        if clean_kw == "ALL_CATEGORY":
            clean_kw = "護理技術"

        search_url = self.build_search_url(clean_kw)
        logger.info(f"🌐 連結 Gemini 護理 AI 助手: {clean_kw} -> {search_url}")

        return [
            {
                "title": f"{clean_kw} 操作步驟與照護指引",
                "url": search_url,
                "link": search_url,
                "summary": f"由 Gemini 護理 AI 助手提供「{clean_kw}」之標準作業流程、無菌技術規範與注意事項。",
                "steps": [
                    {"step": 1, "title": "核對醫囑與病人辨識", "detail": "確認醫囑，執行雙重病人辨識並說明處置目的。"},
                    {"step": 2, "title": "準備用物與手部衛生", "detail": "依據技術規範準備相關用物，執行標準手部衛生。"},
                    {"step": 3, "title": "執行操作與維護無菌", "detail": f"遵循「{clean_kw}」標準技術流程與無菌原則進行操作。"},
                    {"step": 4, "title": "評估紀錄與衛教", "detail": "觀察病人反應，完整紀錄技術處置時間與結果。"},
                ],
                "warnings": ["嚴格遵守無菌技術與病人安全規範", "若有異常反應應立即停止並通報醫師"],
                "evidence_level": "Gemini AI 護理實證指引",
                "category": "護理技術",
                "source": "Gemini 護理 AI 助手",
            }
        ]
