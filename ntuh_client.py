"""
台大醫院藥劑部 (NTUH Pharmacy) 藥品查詢客戶端
===============================================
連線至台大醫院藥劑部「藥品綜合查詢系統」：
https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939
（對應查詢端點：https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx）

可動態檢索台大醫院藥品庫：
- 藥物學名 (Generic Name)
- 中文藥名 (Chinese Brand Name)
- 商品名與劑量規格 (Brand Name & Specification)
- 用藥教育 PDF 衛教單張
- 藥品仿單 PDF 指導說明
"""

import re
import logging
import urllib3
import requests
from typing import List, Dict
from html import unescape

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

NTUH_QUERY_URL = "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"
NTUH_HOME_URL = "https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939"


class NTUHClient:
    """台大醫院藥劑部藥品查詢客戶端"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def search_drug(self, keyword: str) -> List[Dict]:
        """
        搜尋台大醫院藥劑部藥品資料。

        Args:
            keyword: 藥名、學名或適應症關鍵字

        Returns:
            藥物資訊列表
        """
        keyword = keyword.strip()
        if not keyword or keyword == "ALL_CATEGORY":
            keyword = "Metformin"

        try:
            # 1. 取得 ViewState
            resp = self.session.get(NTUH_QUERY_URL, verify=False, timeout=3)
            vs_m = re.search(r'id="__VIEWSTATE"\s+value="([^"]+)"', resp.text)
            gen_m = re.search(r'id="__VIEWSTATEGENERATOR"\s+value="([^"]+)"', resp.text)
            val_m = re.search(r'id="__EVENTVALIDATION"\s+value="([^"]+)"', resp.text)

            if not vs_m:
                logger.warning("無法取得 NTUH ViewState")
                return []

            viewstate = vs_m.group(1)
            generator = gen_m.group(1) if gen_m else ""
            validation = val_m.group(1) if val_m else ""

            # 2. 以「藥名查詢」發送 POST
            payload_name = {
                "__VIEWSTATE": viewstate,
                "__VIEWSTATEGENERATOR": generator,
                "__EVENTVALIDATION": validation,
                "DrugInfoQueryBox$txbDrugName": keyword,
                "DrugInfoQueryBox$btnQueryByDrugName": "查詢",
            }
            post_resp = self.session.post(NTUH_QUERY_URL, data=payload_name, verify=False, timeout=4)
            results = self._parse_html(post_resp.text)

            # 3. 若藥名查詢無結果，試試關鍵字/適應症查詢
            if not results:
                payload_ind = {
                    "__VIEWSTATE": viewstate,
                    "__VIEWSTATEGENERATOR": generator,
                    "__EVENTVALIDATION": validation,
                    "DrugInfoQueryBox$txbIndication": keyword,
                    "DrugInfoQueryBox$btnQueryByIndication": "查詢",
                }
                post_resp2 = self.session.post(NTUH_QUERY_URL, data=payload_ind, verify=False, timeout=4)
                results = self._parse_html(post_resp2.text)

            logger.info(f"NTUH 藥劑部搜尋「{keyword}」找到 {len(results)} 筆結果")
            return results

        except Exception as e:
            logger.error(f"NTUH 藥劑部查詢錯誤: {e}", exc_info=True)
            return []

    def _parse_html(self, html: str) -> List[Dict]:
        """解析 NTUH DrugListBox_grvDrugList 表格"""
        results = []
        if "grvDrugList" not in html:
            return results

        # 找尋所有 tr.tableCell 或 tr.tableCell2
        tr_pattern = re.compile(r'<tr[^>]*class=["\']tableCell2?["\'][^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
        rows = tr_pattern.findall(html)

        for row in rows:
            td_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
            tds = td_pattern.findall(row)

            if len(tds) < 3:
                continue

            # 1. 學名
            generic_name = re.sub(r'<[^>]+>', '', tds[0]).strip()
            generic_name = unescape(generic_name)

            # 2. 中文名
            chinese_name = re.sub(r'<[^>]+>', '', tds[1]).strip()
            chinese_name = unescape(chinese_name)

            # 3. 商品名 & 規格
            brand_name = re.sub(r'<[^>]+>', '', tds[2]).strip()
            brand_name = unescape(brand_name)

            # 4. 用藥教育 PDF
            edu_link = ""
            if len(tds) >= 4:
                edu_m = re.search(r'href=["\']([^"\']+\.pdf)["\']', tds[3], re.IGNORECASE)
                if edu_m:
                    edu_link = edu_m.group(1)

            # 5. 仿單 PDF
            instruction_link = ""
            if len(tds) >= 6:
                inst_m = re.search(r'href=["\']([^"\']+\.pdf)["\']', tds[5], re.IGNORECASE)
                if inst_m:
                    instruction_link = inst_m.group(1)

            link = instruction_link or edu_link or NTUH_HOME_URL

            results.append({
                "title": f"{chinese_name} ({generic_name})",
                "generic_name": generic_name,
                "chinese_name": chinese_name,
                "brand_names": [brand_name],
                "drug_class": "台大醫院藥劑部核可藥品",
                "indication": f"院內品名：{chinese_name}",
                "dosage": f"規格與商品名：{brand_name}",
                "mechanism": "請參考台大醫院藥劑部完整用藥指導或藥品仿單 PDF。",
                "nursing_considerations": [
                    f"中文藥名：{chinese_name}",
                    f"英文學名：{generic_name}",
                    f"商品名與劑量：{brand_name}",
                    "請核對台大醫院三讀五對用藥安全",
                ],
                "source": "台大醫院藥劑部 (NTUH Pharmacy)",
                "link": link,
                "education_pdf": edu_link,
                "instruction_pdf": instruction_link,
                "summary": f"台大醫院用藥資訊 — 中文：{chinese_name} | 學名：{generic_name} | 商品名：{brand_name}",
            })

        return results[:5]
