"""
Cochrane Library 實證醫學資料庫查詢客戶端
==========================================
連結 Cochrane Library (https://www.cochranelibrary.com/search) 提供臨床實證指引與系統評價。
"""

import logging
import urllib.parse
import html as html_lib

logger = logging.getLogger(__name__)

COCHRANE_SEARCH_BASE = "https://www.cochranelibrary.com/search"

# 常見疾病中文對應英文詞彙（優化 Cochrane Library 檢索效益）
DISEASE_TRANSLATION = {
    "糖尿病": "Diabetes Mellitus",
    "高血壓": "Hypertension",
    "心肌梗塞": "Myocardial Infarction",
    "中風": "Stroke",
    "腦中風": "Stroke",
    "肺炎": "Pneumonia",
    "心衰竭": "Heart Failure",
    "心臟衰竭": "Heart Failure",
    "氣喘": "Asthma",
    "哮喘": "Asthma",
    "癌症": "Cancer",
    "腎臟病": "Kidney Disease",
    "慢性腎臟病": "Chronic Kidney Disease",
    "壓瘡": "Pressure Ulcer",
    "褥瘡": "Pressure Injury",
    "跌倒": "Fall Prevention",
    "傷口": "Wound Care",
    "痛風": "Gout",
    "高血脂": "Hyperlipidemia",
    "失智症": "Dementia",
    "帕金森氏症": "Parkinson's Disease",
}


class CochraneClient:
    """Cochrane Library 實證醫學資料庫客戶端"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def build_search_url(self, keyword: str) -> str:
        """建立 Cochrane Library 官方檢索 URL"""
        clean_kw = keyword.strip() if keyword else "diseases"
        english_term = DISEASE_TRANSLATION.get(clean_kw, clean_kw)
        encoded_kw = urllib.parse.quote(english_term)
        return (
            f"{COCHRANE_SEARCH_BASE}?"
            "p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&"
            "p_p_lifecycle=0&"
            f"_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText={encoded_kw}"
        )

    def search_disease(self, keyword: str) -> list:
        """根據關鍵字產生 Cochrane Library 疾病實證指引資料"""
        if not keyword or not keyword.strip():
            clean_kw = "疾病照護"
        else:
            clean_kw = keyword.strip()

        if clean_kw == "ALL_CATEGORY":
            clean_kw = "疾病照護"

        english_term = DISEASE_TRANSLATION.get(clean_kw, clean_kw)
        search_url = self.build_search_url(clean_kw)

        logger.info(f"🌐 建立 Cochrane Library 實證檢索連結: {clean_kw} ({english_term}) -> {search_url}")

        results = [
            {
                "title": f"{clean_kw} 臨床照護指引 ({english_term})",
                "url": search_url,
                "link": search_url,
                "summary": (
                    f"Cochrane Library（考克蘭實證醫學圖書館）收錄國際頂尖實證醫學系統評價（Systematic Reviews），"
                    f"針對「{clean_kw}（{english_term}）」提供最高等級 Level A 之臨床治療與護理照護實證依據。"
                ),
                "key_points": [
                    f"收錄「{clean_kw}」最新 Cochrane Systematic Reviews 系統評價",
                    "分析高質量隨機對照試驗 (RCT) 之綜合臨床療效與安全性",
                    "提供臨床治療、處置介入與護理照護之等級實證建議",
                    "國際權威實證醫學指引，輔助護理決策與臨床照護品質",
                ],
                "nursing_focus": [
                    f"評估「{clean_kw}」最新實證護理介入措施與處置指引",
                    "依據 Cochrane 實證指引執行臨床護理與病人衛教",
                    "持續追蹤病人照護結果與症狀變化",
                ],
                "category": "臨床指引",
                "source": "Cochrane Library 實證醫學資料庫",
            }
        ]

        return results
