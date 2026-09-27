"""
台大醫院藥劑部 (NTUH Pharmacy) API 串接測試
"""

import re
import urllib3
import requests
from html import unescape

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NTUH_URL = "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"

def search_ntuh_pharmacy(keyword: str):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 1. 取得頁面表單 ViewState
    resp = session.get(NTUH_URL, verify=False, timeout=10)
    viewstate_m = re.search(r'id="__VIEWSTATE"\s+value="([^"]+)"', resp.text)
    generator_m = re.search(r'id="__VIEWSTATEGENERATOR"\s+value="([^"]+)"', resp.text)
    validation_m = re.search(r'id="__EVENTVALIDATION"\s+value="([^"]+)"', resp.text)

    if not viewstate_m:
        print("無法取得 ViewState")
        return []

    viewstate = viewstate_m.group(1)
    generator = generator_m.group(1) if generator_m else ""
    validation = validation_m.group(1) if validation_m else ""

    # 2. 發送藥名查詢 POST
    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": generator,
        "__EVENTVALIDATION": validation,
        "DrugInfoQueryBox$txbDrugName": keyword,
        "DrugInfoQueryBox$btnQueryByDrugName": "查詢",
    }

    post_resp = session.post(NTUH_URL, data=payload, verify=False, timeout=15)
    html_text = post_resp.text

    with open("ntuh_result.html", "w", encoding="utf-8") as f:
        f.write(html_text)

    print("已儲存 HTML 至 ntuh_result.html，長度:", len(html_text))

if __name__ == "__main__":
    search_ntuh_pharmacy("Metformin")
