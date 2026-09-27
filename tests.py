"""
NurseBot 護理智慧助手 — 單元測試
=================================
測試指令解析器、模擬資料查詢、Flex Message 建構。
執行：python -m pytest tests.py -v
"""

import json
import pytest
from command_parser import parse_command
from mock_data import MockDataProvider
from flex_builder import FlexBuilder


# =====================================================================
# 指令解析器測試
# =====================================================================
class TestCommandParser:
    """測試 parse_command 函式"""

    def test_nursing_skill_plus(self):
        assert parse_command("護+導尿管置入") == ("nursing_skill", "導尿管置入")

    def test_nursing_skill_fullwidth_plus(self):
        assert parse_command("護＋靜脈注射") == ("nursing_skill", "靜脈注射")

    def test_drug_plus(self):
        assert parse_command("藥+Metformin") == ("drug", "Metformin")

    def test_drug_colon(self):
        assert parse_command("藥：Warfarin") == ("drug", "Warfarin")

    def test_disease_space(self):
        assert parse_command("病 糖尿病") == ("disease", "糖尿病")

    def test_education_plus(self):
        assert parse_command("衛+傷口照護") == ("education", "傷口照護")

    def test_direct_keyword_search(self):
        assert parse_command("導尿管置入") == ("auto", "導尿管置入")

    def test_direct_drug_keyword(self):
        assert parse_command("Metformin") == ("auto", "Metformin")

    def test_category_keywords(self):
        assert parse_command("護理") == ("nursing_skill", "ALL_CATEGORY")
        assert parse_command("藥物") == ("drug", "ALL_CATEGORY")
        assert parse_command("疾病") == ("disease", "ALL_CATEGORY")
        assert parse_command("衛教") == ("education", "ALL_CATEGORY")

    def test_help_command(self):
        assert parse_command("說明") == ("help", "說明")
        assert parse_command("你好") == ("help", "你好")

    def test_empty_string(self):
        assert parse_command("") is None

    def test_prefix_only(self):
        assert parse_command("護+") is None

    def test_whitespace_handling(self):
        result = parse_command("  藥+Insulin  ")
        assert result == ("drug", "Insulin")

    def test_english_colon(self):
        assert parse_command("病:高血壓") == ("disease", "高血壓")


# =====================================================================
# 模擬資料測試
# =====================================================================
class TestMockDataProvider:
    """測試 MockDataProvider 查詢功能"""

    @pytest.fixture
    def provider(self):
        return MockDataProvider()

    def test_nursing_exact_match(self, provider):
        results = provider.search_nursing_skill("導尿管置入")
        assert len(results) >= 1
        assert "導尿" in results[0]["title"]
        assert "Gemini 護理 AI 助手" in results[0]["source"]
        assert "gemini.google.com" in results[0]["link"]

    def test_nursing_alias_match(self, provider):
        results = provider.search_nursing_skill("Foley")
        assert len(results) >= 1

    def test_drug_exact_match(self, provider):
        results = provider.search_drug("Metformin")
        assert len(results) >= 1
        assert "Metformin" in results[0]["title"]

    def test_drug_brand_name(self, provider):
        results = provider.search_drug("Glucophage")
        assert len(results) >= 1

    def test_disease_match(self, provider):
        results = provider.search_disease("糖尿病")
        assert len(results) >= 1
        assert "糖尿病" in results[0]["title"]

    def test_education_match(self, provider):
        results = provider.search_education("傷口照護")
        assert len(results) >= 1

    def test_search_all(self, provider):
        all_res = provider.search_all("糖尿病")
        assert "disease" in all_res or "education" in all_res

    def test_fuzzy_match(self, provider):
        results = provider.search_nursing_skill("導尿")
        assert len(results) >= 1

    def test_drug_has_required_fields(self, provider):
        results = provider.search_drug("Insulin")
        assert len(results) >= 1
        drug = results[0]
        assert "title" in drug
        assert "generic_name" in drug
        assert "drug_class" in drug
        assert "nursing_considerations" in drug

    def test_nursing_has_steps(self, provider):
        results = provider.search_nursing_skill("靜脈注射")
        assert len(results) >= 1


class TestNTUHClient:
    """測試台大醫院藥劑部 NTUHClient 客戶端"""

    def test_ntuh_search_metformin(self):
        from ntuh_client import NTUHClient
        client = NTUHClient()
        results = client.search_drug("Metformin")
        assert len(results) >= 1
        assert "Metformin" in results[0]["generic_name"] or "庫魯化" in results[0]["chinese_name"]
        assert "台大醫院藥劑部" in results[0]["source"]

    def test_ntuh_search_aspirin(self):
        from ntuh_client import NTUHClient
        client = NTUHClient()
        results = client.search_drug("Aspirin")
        assert len(results) >= 1
        assert "Aspirin" in results[0]["generic_name"] or "阿斯匹靈" in results[0]["title"] or "伯基" in results[0]["title"]


class TestCareOnlineClient:
    """測試照護線上 CareOnlineClient 客戶端"""

    def test_careonline_search_wound(self):
        from careonline_client import CareOnlineClient
        client = CareOnlineClient()
        results = client.search_education("傷口照護")
        assert len(results) >= 1
        assert "careonline.com.tw" in results[0]["url"]
        assert "utm_source=gemini" in results[0]["url"]
        assert "照護線上 CareOnline" in results[0]["source"]

    def test_careonline_search_diabetes(self):
        from careonline_client import CareOnlineClient
        client = CareOnlineClient()
        results = client.search_education("糖尿病")
        assert len(results) >= 1
        assert "careonline.com.tw" in results[0]["url"]


class TestCochraneClient:
    """測試 Cochrane Library 實證醫學圖書館客戶端"""

    def test_cochrane_search_diabetes(self):
        from cochrane_client import CochraneClient
        client = CochraneClient()
        results = client.search_disease("糖尿病")
        assert len(results) >= 1
        assert "cochranelibrary.com" in results[0]["url"]
        assert "Diabetes+Mellitus" in results[0]["url"] or "Diabetes" in results[0]["url"]
        assert "Cochrane Library" in results[0]["source"]

    def test_cochrane_search_hypertension(self):
        from cochrane_client import CochraneClient
        client = CochraneClient()
        results = client.search_disease("高血壓")
        assert len(results) >= 1
        assert "cochranelibrary.com" in results[0]["url"]


class TestGeminiClient:
    """測試 Gemini 護理 AI 助手客戶端"""

    def test_gemini_search_nursing_skill(self):
        from gemini_client import GeminiClient
        client = GeminiClient()
        results = client.search_nursing_skill("導尿管置入")
        assert len(results) >= 1
        assert "gemini.google.com" in results[0]["url"]
        assert "Gemini 護理 AI 助手" in results[0]["source"]


# =====================================================================
# Flex Builder 測試
# =====================================================================
class TestFlexBuilder:
    """測試 FlexBuilder 產生的 JSON 結構"""

    @pytest.fixture
    def builder(self):
        return FlexBuilder()

    @pytest.fixture
    def provider(self):
        return MockDataProvider()

    def test_nursing_single_bubble(self, builder, provider):
        results = provider.search_nursing_skill("導尿管置入")
        flex = builder.build_nursing_skill_card("導尿管置入", results)
        assert flex["type"] == "bubble"
        assert "body" in flex
        # 確認可序列化為 JSON
        json_str = json.dumps(flex, ensure_ascii=False)
        assert len(json_str) < 50000  # Flex Message 限制 50KB

    def test_drug_single_bubble(self, builder, provider):
        results = provider.search_drug("Metformin")
        flex = builder.build_drug_card("Metformin", results)
        assert flex["type"] == "bubble"

    def test_disease_single_bubble(self, builder, provider):
        results = provider.search_disease("糖尿病")
        flex = builder.build_disease_card("糖尿病", results)
        assert flex["type"] == "bubble"

    def test_education_single_bubble(self, builder, provider):
        results = provider.search_education("傷口照護")
        flex = builder.build_education_card("傷口照護", results)
        assert flex["type"] == "bubble"

    def test_multi_result_carousel(self, builder):
        # 模擬多筆結果
        fake_results = [
            {"title": "結果1", "summary": "摘要1", "source": "DynaMed", "link": "https://example.com"},
            {"title": "結果2", "summary": "摘要2", "source": "DynaMed", "link": "https://example.com"},
        ]
        flex = builder.build_drug_card("test", fake_results)
        assert flex["type"] == "carousel"
        assert len(flex["contents"]) == 2

    def test_flex_json_serializable(self, builder, provider):
        """確認所有類型的 Flex Message 都可以正確序列化"""
        results_nursing = provider.search_nursing_skill("CPR")
        results_drug = provider.search_drug("Digoxin")
        results_disease = provider.search_disease("中風")
        results_edu = provider.search_education("跌倒預防")

        for results, build_fn in [
            (results_nursing, builder.build_nursing_skill_card),
            (results_drug, builder.build_drug_card),
            (results_disease, builder.build_disease_card),
            (results_edu, builder.build_education_card),
        ]:
            flex = build_fn("test", results)
            json_str = json.dumps(flex, ensure_ascii=False)
            parsed = json.loads(json_str)
            assert parsed is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
