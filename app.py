"""
LINE 護理智慧助手 — NurseBot
============================
護理人員專用的 LINE 聊天機器人，支援即時查詢：
  護+主題  → 護理技術操作步驟 (Gemini 護理 AI 助手)
  藥+學名  → 藥物資訊查詢   (台大醫院藥劑部 NTUH Pharmacy)
  病+疾病  → 臨床照護指引   (Cochrane Library 實證醫學圖書館)
  衛+主題  → 衛教單張查詢   (照護線上 CareOnline)

串接即時網頁資料庫與 API，回傳標準化 Flex Message 卡片。
"""

import os
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from command_parser import parse_command
from ebsco_client import EBSCOClient
from flex_builder import FlexBuilder
from mock_data import MockDataProvider
from ntuh_client import NTUHClient
from careonline_client import CareOnlineClient
from cochrane_client import CochraneClient
from gemini_client import GeminiClient

# ---------------------------------------------------------------------------
# 初始化
# ---------------------------------------------------------------------------
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# LINE Bot 設定
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# EBSCO / NTUH / CareOnline / Cochrane / Gemini 資料庫設定
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

if USE_MOCK_DATA:
    logger.info("🔧 使用 Gemini 護理 AI 助手 + 🏥 台大醫院藥劑部 + 💚 照護線上 + 📚 Cochrane Library 模式")
    raw_provider = MockDataProvider()
else:
    logger.info("🌐 使用 EBSCO EDS + 🏥 台大醫院藥劑部 + 💚 照護線上 + 📚 Cochrane Library 模式")
    raw_provider = EBSCOClient(
        profile_id=os.getenv("EBSCO_PROFILE_ID", ""),
        user_id=os.getenv("EBSCO_USER_ID", ""),
        password=os.getenv("EBSCO_PASSWORD", ""),
    )


class SmartNurseDataProvider:
    """整合台大醫院藥劑部 (NTUH Pharmacy)、照護線上 (CareOnline)、Cochrane Library 與 Gemini 護理 AI 助手 (平行檢索 + 高速快取)"""

    def __init__(self, base_provider):
        self.base_provider = base_provider
        self.ntuh = NTUHClient()
        self.careonline = CareOnlineClient()
        self.cochrane = CochraneClient()
        self.gemini = GeminiClient()
        self._cache = {}
        self._cache_ttl = 600  # 10 分鐘快取

    def _get_cache(self, key: str):
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                logger.info(f"⚡ 觸發高速快取命中: {key}")
                return data
        return None

    def _set_cache(self, key: str, data):
        self._cache[key] = (data, time.time())

    def search_drug(self, keyword: str) -> list:
        cache_key = f"drug_{keyword}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        logger.info(f"🔍 向台大醫院藥劑部資料庫查詢藥品: {keyword}")
        try:
            ntuh_results = self.ntuh.search_drug(keyword)
            if ntuh_results:
                self._set_cache(cache_key, ntuh_results)
                return ntuh_results
        except Exception as e:
            logger.warning(f"台大醫院藥劑部查詢例外: {e}")

        logger.info(f"台大醫院藥劑部查無「{keyword}」，改用備用資料庫")
        try:
            results = self.base_provider.search_drug(keyword)
            self._set_cache(cache_key, results)
            return results
        except Exception as e:
            logger.warning(f"備用藥物資料庫查詢失敗: {e}")
            return []

    def search_nursing_skill(self, keyword: str) -> list:
        cache_key = f"nursing_{keyword}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        logger.info(f"🔍 向 Gemini 護理 AI 助手查詢護理技術: {keyword}")
        try:
            results = self.base_provider.search_nursing_skill(keyword)
            if results:
                self._set_cache(cache_key, results)
                return results
        except Exception as e:
            logger.warning(f"基礎護理資料庫查詢例外 ({e})，自動切換至 Gemini 護理 AI 助手")

        results = self.gemini.search_nursing_skill(keyword)
        self._set_cache(cache_key, results)
        return results

    def search_disease(self, keyword: str) -> list:
        cache_key = f"disease_{keyword}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        logger.info(f"🔍 向 Cochrane Library 實證醫學資料庫查詢疾病: {keyword}")
        cochrane_results = self.cochrane.search_disease(keyword)
        if cochrane_results:
            self._set_cache(cache_key, cochrane_results)
            return cochrane_results
        
        fallback = self.cochrane.search_disease("diseases")
        self._set_cache(cache_key, fallback)
        return fallback

    def search_education(self, keyword: str) -> list:
        cache_key = f"education_{keyword}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        logger.info(f"🔍 向照護線上 CareOnline 查詢衛教單張: {keyword}")
        care_results = self.careonline.search_education(keyword)
        if care_results:
            self._set_cache(cache_key, care_results)
            return care_results

        fallback = self.careonline.search_education("衛教")
        self._set_cache(cache_key, fallback)
        return fallback

    def search_all(self, keyword: str) -> dict:
        cache_key = f"all_{keyword}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        results = {}
        tasks = {
            "nursing_skill": lambda: self.search_nursing_skill(keyword),
            "drug": lambda: self.search_drug(keyword),
            "disease": lambda: self.search_disease(keyword),
            "education": lambda: self.search_education(keyword),
        }

        # ⚡ 多執行緒平行同步檢索四大資料庫
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_cat = {executor.submit(fn): cat for cat, fn in tasks.items()}
            for future in as_completed(future_to_cat):
                cat = future_to_cat[future]
                try:
                    res = future.result()
                    if res:
                        results[cat] = res
                except Exception as e:
                    logger.warning(f"平行搜尋 {cat} 失敗: {e}")

        self._set_cache(cache_key, results)
        return results


data_provider = SmartNurseDataProvider(raw_provider)
flex_builder = FlexBuilder()


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """護理智慧查詢網 首頁 SPA"""
    return render_template("index.html")


@app.route("/api/search", methods=["GET"])
def api_search():
    """Web 智慧搜尋 API"""
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "all").strip()

    if not keyword:
        return jsonify({})

    logger.info(f"🌐 Web API 搜尋: {keyword} (類別: {category})")

    if category == "all" or not category:
        results = data_provider.search_all(keyword)
    elif category == "nursing_skill":
        results = {"nursing_skill": data_provider.search_nursing_skill(keyword)}
    elif category == "drug":
        results = {"drug": data_provider.search_drug(keyword)}
    elif category == "disease":
        results = {"disease": data_provider.search_disease(keyword)}
    elif category == "education":
        results = {"education": data_provider.search_education(keyword)}
    else:
        results = data_provider.search_all(keyword)

    return jsonify(results)



@app.route("/callback", methods=["POST"])
def callback():
    """LINE Webhook 回呼端點"""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logger.info("收到 Webhook 請求")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("簽章驗證失敗")
        abort(400)

    return "OK"


# ---------------------------------------------------------------------------
# 訊息處理
# ---------------------------------------------------------------------------
HELP_TEXT = (
    "🏥 護理智慧查詢助手\n"
    "━━━━━━━━━━━━━━━\n"
    "💡 直接輸入關鍵字即可全庫查詢！\n"
    "   例如：\n"
    "   • 導尿管 / 靜脈注射 / CPR\n"
    "   • Metformin / 普拿疼 / 阿斯匹靈\n"
    "   • 糖尿病 / 心肌梗塞 / 中風\n"
    "   • 傷口照護 / 跌倒預防 / 換藥\n\n"
    "🎯 亦可使用前綴精準指定：\n"
    "   🩺 護+主題 (護理技術)\n"
    "   💊 藥+學名 (台大藥劑部)\n"
    "   📋 病+疾病 (Cochrane Library 實證指引)\n"
    "   📄 衛+主題 (照護線上 CareOnline)\n"
    "━━━━━━━━━━━━━━━\n"
    "輸入「說明」可再次查看此選單"
)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理使用者文字訊息"""
    user_text = event.message.text.strip()
    logger.info(f"使用者輸入: {user_text}")

    # 解析指令
    cmd = parse_command(user_text)
    if cmd is None:
        _reply_text(event, HELP_TEXT)
        return

    cmd_type, keyword = cmd
    logger.info(f"指令類型: {cmd_type}, 關鍵字: {keyword}")

    if cmd_type == "help":
        _reply_text(event, HELP_TEXT)
        return

    try:
        flex_messages = []

        if cmd_type == "auto":
            # 自動全庫智慧搜尋
            all_results = data_provider.search_all(keyword)
            if not all_results:
                _reply_text(
                    event,
                    f"🔍 查無「{keyword}」相關資料。\n\n"
                    "💡 建議試試以下示範關鍵字：\n"
                    "• 護理技術：導尿管、靜脈注射、鼻胃管、抽血、CPR\n"
                    "• 藥物資訊：Metformin、普拿疼、Aspirin、胰島素\n"
                    "• 臨床疾病：糖尿病、心肌梗塞、中風、高血壓\n"
                    "• 衛教單張：傷口照護、跌倒預防、壓瘡預防"
                )
                return

            # 為所有比對到的類別建立 Flex 卡片
            for cat, results in all_results.items():
                if cat == "nursing_skill":
                    card = flex_builder.build_nursing_skill_card(keyword, results)
                    flex_messages.append((f"技術操作：{keyword}", card))
                elif cat == "drug":
                    card = flex_builder.build_drug_card(keyword, results)
                    flex_messages.append((f"藥物資訊：{keyword}", card))
                elif cat == "disease":
                    card = flex_builder.build_disease_card(keyword, results)
                    flex_messages.append((f"疾病指引：{keyword}", card))
                elif cat == "education":
                    card = flex_builder.build_education_card(keyword, results)
                    flex_messages.append((f"衛教單張：{keyword}", card))

        else:
            # 前綴精準搜尋
            results = []
            flex_fn = None
            if cmd_type == "nursing_skill":
                results = data_provider.search_nursing_skill(keyword)
                flex_fn = flex_builder.build_nursing_skill_card
            elif cmd_type == "drug":
                results = data_provider.search_drug(keyword)
                flex_fn = flex_builder.build_drug_card
            elif cmd_type == "disease":
                results = data_provider.search_disease(keyword)
                flex_fn = flex_builder.build_disease_card
            elif cmd_type == "education":
                results = data_provider.search_education(keyword)
                flex_fn = flex_builder.build_education_card

            if results and flex_fn:
                card = flex_fn(keyword, results)
                flex_messages.append((f"查詢結果：{keyword}", card))
            else:
                # 備案：嘗試全庫搜尋
                all_results = data_provider.search_all(keyword)
                if all_results:
                    for cat, res in all_results.items():
                        if cat == "nursing_skill":
                            card = flex_builder.build_nursing_skill_card(keyword, res)
                        elif cat == "drug":
                            card = flex_builder.build_drug_card(keyword, res)
                        elif cat == "disease":
                            card = flex_builder.build_disease_card(keyword, res)
                        else:
                            card = flex_builder.build_education_card(keyword, res)
                        flex_messages.append((f"查詢結果：{keyword}", card))

        if not flex_messages:
            _reply_text(
                event,
                f"🔍 查無「{keyword}」相關資料。\n\n"
                "建議直接輸入關鍵字，如：導尿管、糖尿病、Metformin、傷口照護。"
            )
            return

        # 發送 Flex Messages (最多 5 個)
        _reply_flex_list(event, flex_messages)

    except Exception as e:
        logger.error(f"查詢錯誤: {e}", exc_info=True)
        _reply_text(
            event,
            "⚠️ 查詢時發生錯誤，請稍後再試。\n"
            f"錯誤訊息：{str(e)[:100]}"
        )


# ---------------------------------------------------------------------------
# 回覆輔助函式
# ---------------------------------------------------------------------------
def _reply_text(event, text: str):
    """回覆純文字訊息"""
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)],
            )
        )


def _reply_flex(event, alt_text: str, flex_json: dict):
    """回覆單一 Flex Message"""
    _reply_flex_list(event, [(alt_text, flex_json)])


def _reply_flex_list(event, flex_items: list):
    """回覆一或多個 Flex Message（最多 5 個）"""
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        messages = []
        for alt_text, flex_json in flex_items[:5]:
            container = FlexContainer.from_json(json.dumps(flex_json))
            messages.append(FlexMessage(alt_text=alt_text, contents=container))
        api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages,
            )
        )


# ---------------------------------------------------------------------------
# 啟動
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
