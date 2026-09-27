"""
EBSCO Discovery Service (EDS) API 客戶端
=========================================
透過 EBSCO EDS REST API 查詢 DynaMed 與 Dynamic Health 資料庫。

⚠️ 使用此模組需要有效的 EBSCO API 帳號：
   - Profile ID
   - User ID (API 用途)
   - Password

若尚未取得帳號，請設定 USE_MOCK_DATA=true 使用模擬資料模式。
"""

import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# EDS API 端點
EDS_AUTH_URL = "https://eds-api.ebscohost.com/authservice/rest/UIDAuth"
EDS_SESSION_URL = "https://eds-api.ebscohost.com/edsapi/rest/CreateSession"
EDS_SEARCH_URL = "https://eds-api.ebscohost.com/edsapi/rest/Search"
EDS_RETRIEVE_URL = "https://eds-api.ebscohost.com/edsapi/rest/Retrieve"

# 資料庫代碼
DB_DYNAMED = "dnh"           # DynaMed
DB_DYNAMIC_HEALTH = "dih"    # Dynamic Health


class EBSCOClient:
    """EBSCO EDS API 客戶端"""

    def __init__(self, profile_id: str, user_id: str, password: str):
        self.profile_id = profile_id
        self.user_id = user_id
        self.password = password
        self._auth_token: Optional[str] = None
        self._session_token: Optional[str] = None

    # ------------------------------------------------------------------
    # 認證與連線管理
    # ------------------------------------------------------------------
    def _authenticate(self) -> str:
        """取得 Authentication Token"""
        if self._auth_token:
            return self._auth_token

        payload = {
            "UserId": self.user_id,
            "Password": self.password,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            resp = requests.post(EDS_AUTH_URL, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._auth_token = data.get("AuthToken")
            logger.info("EDS 認證成功")
            return self._auth_token
        except Exception as e:
            logger.error(f"EDS 認證失敗: {e}")
            raise ConnectionError(f"無法連線到 EBSCO 認證服務: {e}")

    def _create_session(self) -> str:
        """建立 EDS Session"""
        if self._session_token:
            return self._session_token

        auth_token = self._authenticate()
        payload = {
            "Profile": self.profile_id,
            "Guest": "n",
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-authenticationToken": auth_token,
        }

        try:
            resp = requests.post(EDS_SESSION_URL, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self._session_token = data.get("SessionToken")
            logger.info("EDS Session 建立成功")
            return self._session_token
        except Exception as e:
            logger.error(f"EDS Session 建立失敗: {e}")
            raise ConnectionError(f"無法建立 EDS Session: {e}")

    def _get_headers(self) -> dict:
        """取得 API 請求標頭"""
        auth_token = self._authenticate()
        session_token = self._create_session()
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-authenticationToken": auth_token,
            "x-sessionToken": session_token,
        }

    def _reset_session(self):
        """重設 Session（Token 過期時使用）"""
        self._auth_token = None
        self._session_token = None

    # ------------------------------------------------------------------
    # 搜尋方法
    # ------------------------------------------------------------------
    def _search(self, query: str, database: str, num_results: int = 5) -> List[Dict]:
        """
        執行 EDS 搜尋查詢。

        Args:
            query: 搜尋關鍵字
            database: 資料庫代碼 (dnh=DynaMed, dih=Dynamic Health)
            num_results: 回傳筆數上限

        Returns:
            搜尋結果列表
        """
        try:
            headers = self._get_headers()
        except ConnectionError:
            # 認證失敗時重試一次
            self._reset_session()
            headers = self._get_headers()

        params = {
            "query": f"TI:{query} OR SU:{query}",
            "searchmode": "all",
            "resultsperpage": str(num_results),
            "pagenumber": "1",
            "sort": "relevance",
            "highlight": "n",
            "includefacets": "n",
            "limiter": f"DB:{database}" if database else "",
        }

        try:
            resp = requests.get(EDS_SEARCH_URL, params=params, headers=headers, timeout=15)

            # Session 過期時重試
            if resp.status_code == 400:
                self._reset_session()
                headers = self._get_headers()
                resp = requests.get(EDS_SEARCH_URL, params=params, headers=headers, timeout=15)

            resp.raise_for_status()
            data = resp.json()

            results = []
            search_result = data.get("SearchResult", {})
            records = search_result.get("Data", {}).get("Records", [])

            for record in records[:num_results]:
                result = self._parse_record(record)
                if result:
                    results.append(result)

            logger.info(f"EDS 搜尋「{query}」找到 {len(results)} 筆結果")
            return results

        except Exception as e:
            logger.error(f"EDS 搜尋錯誤: {e}")
            raise RuntimeError(f"搜尋「{query}」時發生錯誤: {e}")

    def _parse_record(self, record: dict) -> Optional[Dict]:
        """解析單筆 EDS 搜尋結果"""
        try:
            header = record.get("Header", {})
            items = record.get("Items", [])

            title = ""
            abstract = ""
            for item in items:
                if item.get("Name") == "Title":
                    title = self._clean_html(item.get("Data", ""))
                elif item.get("Name") == "Abstract":
                    abstract = self._clean_html(item.get("Data", ""))

            if not title:
                title = header.get("PublicationTitle", "未知標題")

            # 建構結果直連 URL
            db_id = header.get("DbId", "")
            an = header.get("An", "")
            link = f"https://search.ebscohost.com/login.aspx?direct=true&db={db_id}&AN={an}"

            return {
                "title": title,
                "abstract": abstract[:200] if abstract else "",
                "source": header.get("DbLabel", "EBSCO"),
                "link": link,
                "db_id": db_id,
                "an": an,
            }
        except Exception as e:
            logger.warning(f"解析記錄時發生錯誤: {e}")
            return None

    @staticmethod
    def _clean_html(text: str) -> str:
        """移除 HTML 標籤"""
        import re
        clean = re.sub(r"<[^>]+>", "", text)
        return clean.strip()

    # ------------------------------------------------------------------
    # 公開介面（與 MockDataProvider 相同簽章）
    # ------------------------------------------------------------------
    def search_all(self, keyword: str) -> Dict[str, List[Dict]]:
        """全庫搜尋，回傳各類別結果字典"""
        results = {}
        for cat, search_fn in [
            ("nursing_skill", self.search_nursing_skill),
            ("drug", self.search_drug),
            ("disease", self.search_disease),
            ("education", self.search_education),
        ]:
            try:
                res = search_fn(keyword)
                if res:
                    results[cat] = res
            except Exception as e:
                logger.warning(f"EBSCO 搜尋 {cat} 失敗: {e}")
        return results

    def search_nursing_skill(self, keyword: str) -> List[Dict]:
        """搜尋護理技術操作（Gemini 護理 AI 助手）"""
        q = "nursing skills" if keyword == "ALL_CATEGORY" else keyword
        results = self._search(q, database=DB_DYNAMIC_HEALTH)
        for r in results:
            r["source"] = "Gemini 護理 AI 助手"
            r["link"] = "https://gemini.google.com/app"
            r["url"] = "https://gemini.google.com/app"
        return results

    def search_drug(self, keyword: str) -> List[Dict]:
        """搜尋藥物資訊（DynaMed）"""
        q = "pharmaceuticals" if keyword == "ALL_CATEGORY" else keyword
        return self._search(q, database=DB_DYNAMED)

    def search_disease(self, keyword: str) -> List[Dict]:
        """搜尋疾病照護指引（DynaMed）"""
        q = "diseases" if keyword == "ALL_CATEGORY" else keyword
        return self._search(q, database=DB_DYNAMED)

    def search_education(self, keyword: str) -> List[Dict]:
        """搜尋衛教單張（照護線上 CareOnline）"""
        q = "patient education" if keyword == "ALL_CATEGORY" else keyword
        return self._search(q, database=DB_DYNAMIC_HEALTH)
