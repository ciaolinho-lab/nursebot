"""
Flex Message 建構器
===================
將查詢結果轉換為美觀的 LINE Flex Message JSON 結構。
支援四種卡片類型：護理技術、藥物資訊、疾病指引、衛教單張。

設計原則：
- 使用 Bubble 呈現主要內容 + 步驟摘要
- 步驟超過限制時使用摺疊呈現
- 多筆結果使用 Carousel 橫向瀏覽
- 底部附上「查看完整內容」連結按鈕
"""

import json
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# 配色方案
# ---------------------------------------------------------------------------
COLORS = {
    "nursing": {
        "primary": "#00B894",       # 薄荷綠
        "secondary": "#55EFC4",
        "bg": "#FAFFFE",
        "badge": "#00B894",
        "badge_text": "#FFFFFF",
    },
    "drug": {
        "primary": "#6C5CE7",       # 靛藍紫
        "secondary": "#A29BFE",
        "bg": "#FAF9FF",
        "badge": "#6C5CE7",
        "badge_text": "#FFFFFF",
    },
    "disease": {
        "primary": "#E17055",       # 珊瑚橘
        "secondary": "#FAB1A0",
        "bg": "#FFFAF9",
        "badge": "#E17055",
        "badge_text": "#FFFFFF",
    },
    "education": {
        "primary": "#0984E3",       # 寶藍
        "secondary": "#74B9FF",
        "bg": "#F8FCFF",
        "badge": "#0984E3",
        "badge_text": "#FFFFFF",
    },
}

ICON_MAP = {
    "nursing": "🩺",
    "drug": "💊",
    "disease": "📋",
    "education": "📄",
}


class FlexBuilder:
    """建構 LINE Flex Message JSON"""

    # ==================================================================
    # 公開介面
    # ==================================================================
    def build_nursing_skill_card(self, keyword: str, results: List[Dict]) -> dict:
        """建構護理技術操作卡片"""
        if len(results) == 1:
            return self._single_nursing_bubble(results[0])
        return self._multi_result_carousel(results, "nursing")

    def build_drug_card(self, keyword: str, results: List[Dict]) -> dict:
        """建構藥物資訊卡片"""
        if len(results) == 1:
            return self._single_drug_bubble(results[0])
        return self._multi_result_carousel(results, "drug")

    def build_disease_card(self, keyword: str, results: List[Dict]) -> dict:
        """建構疾病照護指引卡片"""
        if len(results) == 1:
            return self._single_disease_bubble(results[0])
        return self._multi_result_carousel(results, "disease")

    def build_education_card(self, keyword: str, results: List[Dict]) -> dict:
        """建構衛教單張卡片"""
        if len(results) == 1:
            return self._single_education_bubble(results[0])
        return self._multi_result_carousel(results, "education")

    # ==================================================================
    # 護理技術 Bubble
    # ==================================================================
    def _single_nursing_bubble(self, data: dict) -> dict:
        colors = COLORS["nursing"]
        steps = data.get("steps", [])
        warnings = data.get("warnings", [])

        # 步驟內容
        step_contents = []
        for s in steps[:8]:
            step_contents.append(self._step_box(
                step_num=s["step"],
                title=s["title"],
                detail=s.get("detail", ""),
                color=colors["primary"],
            ))

        # 警語
        warning_contents = []
        if warnings:
            warning_contents.append({
                "type": "text",
                "text": "⚠️ 注意事項",
                "weight": "bold",
                "size": "sm",
                "color": "#E74C3C",
                "margin": "lg",
            })
            for w in warnings[:4]:
                warning_contents.append({
                    "type": "text",
                    "text": f"• {w}",
                    "size": "xs",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "sm",
                })

        body_contents = [
            # 類別標籤
            self._badge("🩺 護理技術", colors["badge"], colors["badge_text"]),
            # 標題
            {
                "type": "text",
                "text": data.get("title", "護理技術操作"),
                "weight": "bold",
                "size": "lg",
                "color": "#1A1A1A",
                "wrap": True,
                "margin": "md",
            },
            # 摘要
            {
                "type": "text",
                "text": data.get("summary", ""),
                "size": "xs",
                "color": "#888888",
                "wrap": True,
                "margin": "sm",
            },
            # 分隔線
            self._separator(),
            # 證據等級
        ]

        if data.get("evidence_level"):
            body_contents.append({
                "type": "text",
                "text": f"📊 {data['evidence_level']}",
                "size": "xxs",
                "color": colors["primary"],
                "margin": "md",
                "weight": "bold",
            })

        # 步驟標題
        body_contents.append({
            "type": "text",
            "text": "📝 操作步驟",
            "weight": "bold",
            "size": "sm",
            "color": "#333333",
            "margin": "lg",
        })
        body_contents.extend(step_contents)
        body_contents.extend(warning_contents)

        # 資料來源
        body_contents.append(self._source_text(data.get("source", "Gemini 護理 AI 助手")))

        target_url = data.get("link") or data.get("url") or "https://gemini.google.com/app"

        return {
            "type": "bubble",
            "size": "mega",
            "header": self._header_box(colors["primary"], colors["secondary"]),
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents,
                "spacing": "none",
                "paddingAll": "16px",
                "backgroundColor": colors["bg"],
            },
            "footer": self._footer_box(target_url, "查看完整操作步驟", colors["primary"]),
        }

    # ==================================================================
    # 藥物資訊 Bubble
    # ==================================================================
    def _single_drug_bubble(self, data: dict) -> dict:
        colors = COLORS["drug"]

        body_contents = [
            self._badge("💊 藥物資訊", colors["badge"], colors["badge_text"]),
            {
                "type": "text",
                "text": data.get("title", "藥物查詢"),
                "weight": "bold",
                "size": "lg",
                "color": "#1A1A1A",
                "wrap": True,
                "margin": "md",
            },
        ]

        # 基本資訊區塊
        info_pairs = [
            ("學名", data.get("generic_name", "")),
            ("藥理分類", data.get("drug_class", "")),
            ("適應症", data.get("indication", "")),
            ("作用機轉", data.get("mechanism", "")),
            ("劑量", data.get("dosage", "")),
        ]

        for label, value in info_pairs:
            if value:
                body_contents.append(self._info_row(label, value, colors["primary"]))

        # 商品名
        brand_names = data.get("brand_names", [])
        if brand_names:
            body_contents.append(self._info_row("商品名", "、".join(brand_names), colors["primary"]))

        body_contents.append(self._separator())

        # 副作用
        side_effects = data.get("side_effects", [])
        if side_effects:
            body_contents.append({
                "type": "text",
                "text": "⚡ 副作用",
                "weight": "bold",
                "size": "sm",
                "color": "#E74C3C",
                "margin": "md",
            })
            for se in side_effects[:5]:
                body_contents.append({
                    "type": "text",
                    "text": f"• {se}",
                    "size": "xs",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "xs",
                })

        # 禁忌症
        contras = data.get("contraindications", [])
        if contras:
            body_contents.append({
                "type": "text",
                "text": "🚫 禁忌症",
                "weight": "bold",
                "size": "sm",
                "color": "#E74C3C",
                "margin": "md",
            })
            for c in contras[:4]:
                body_contents.append({
                    "type": "text",
                    "text": f"• {c}",
                    "size": "xs",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "xs",
                })

        # 護理重點
        nursing = data.get("nursing_considerations", [])
        if nursing:
            body_contents.append(self._separator())
            body_contents.append({
                "type": "text",
                "text": "🏥 護理重點",
                "weight": "bold",
                "size": "sm",
                "color": colors["primary"],
                "margin": "md",
            })
            for n in nursing[:6]:
                body_contents.append({
                    "type": "text",
                    "text": f"✓ {n}",
                    "size": "xs",
                    "color": "#444444",
                    "wrap": True,
                    "margin": "xs",
                })

        body_contents.append(self._source_text(data.get("source", "DynaMed")))

        return {
            "type": "bubble",
            "size": "mega",
            "header": self._header_box(colors["primary"], colors["secondary"]),
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents,
                "spacing": "none",
                "paddingAll": "16px",
                "backgroundColor": colors["bg"],
            },
            "footer": self._footer_box(data.get("link", "#"), "查看完整藥物資訊", colors["primary"]),
        }

    # ==================================================================
    # 疾病照護 Bubble
    # ==================================================================
    def _single_disease_bubble(self, data: dict) -> dict:
        colors = COLORS["disease"]

        body_contents = [
            self._badge("📋 臨床照護指引", colors["badge"], colors["badge_text"]),
            {
                "type": "text",
                "text": data.get("title", "疾病查詢"),
                "weight": "bold",
                "size": "lg",
                "color": "#1A1A1A",
                "wrap": True,
                "margin": "md",
            },
            {
                "type": "text",
                "text": data.get("summary", ""),
                "size": "xs",
                "color": "#888888",
                "wrap": True,
                "margin": "sm",
            },
            self._separator(),
        ]

        # 重點摘要
        key_points = data.get("key_points", [])
        if key_points:
            body_contents.append({
                "type": "text",
                "text": "🔑 重點摘要",
                "weight": "bold",
                "size": "sm",
                "color": colors["primary"],
                "margin": "md",
            })
            for kp in key_points[:6]:
                body_contents.append({
                    "type": "text",
                    "text": f"• {kp}",
                    "size": "xs",
                    "color": "#444444",
                    "wrap": True,
                    "margin": "sm",
                })

        # 護理焦點
        nursing_focus = data.get("nursing_focus", [])
        if nursing_focus:
            body_contents.append(self._separator())
            body_contents.append({
                "type": "text",
                "text": "🏥 護理焦點",
                "weight": "bold",
                "size": "sm",
                "color": colors["primary"],
                "margin": "md",
            })
            for nf in nursing_focus[:7]:
                body_contents.append({
                    "type": "text",
                    "text": f"✓ {nf}",
                    "size": "xs",
                    "color": "#444444",
                    "wrap": True,
                    "margin": "xs",
                })

        body_contents.append(self._source_text(data.get("source", "Cochrane Library 實證醫學資料庫")))

        target_url = data.get("url") or data.get("link") or "#"

        return {
            "type": "bubble",
            "size": "mega",
            "header": self._header_box(colors["primary"], colors["secondary"]),
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents,
                "spacing": "none",
                "paddingAll": "16px",
                "backgroundColor": colors["bg"],
            },
            "footer": self._footer_box(target_url, "查看完整照護指引", colors["primary"]),
        }

    # ==================================================================
    # 衛教單張 Bubble
    # ==================================================================
    def _single_education_bubble(self, data: dict) -> dict:
        colors = COLORS["education"]

        body_contents = [
            self._badge("📄 衛教單張", colors["badge"], colors["badge_text"]),
            {
                "type": "text",
                "text": data.get("title", "衛教查詢"),
                "weight": "bold",
                "size": "lg",
                "color": "#1A1A1A",
                "wrap": True,
                "margin": "md",
            },
            {
                "type": "text",
                "text": f"👤 對象：{data.get('target_audience', '病人與家屬')}",
                "size": "xs",
                "color": "#888888",
                "margin": "sm",
            },
            self._separator(),
        ]

        # 衛教內容摘要 (如有)
        summary_text = data.get("summary") or data.get("snippet")
        if summary_text:
            body_contents.append({
                "type": "text",
                "text": summary_text,
                "size": "sm",
                "color": "#444444",
                "wrap": True,
                "margin": "md",
            })

        # 衛教內容各段落
        content_sections = data.get("content", [])
        for section in content_sections[:5]:
            body_contents.append({
                "type": "text",
                "text": f"📌 {section.get('section', '')}",
                "weight": "bold",
                "size": "sm",
                "color": colors["primary"],
                "margin": "lg",
            })
            for point in section.get("points", [])[:4]:
                body_contents.append({
                    "type": "text",
                    "text": f"• {point}",
                    "size": "xs",
                    "color": "#444444",
                    "wrap": True,
                    "margin": "xs",
                })

        body_contents.append(self._source_text(data.get("source", "照護線上 CareOnline")))

        target_url = data.get("url") or data.get("link") or "#"

        bubble = {
            "type": "bubble",
            "size": "mega",
            "header": self._header_box(colors["primary"], colors["secondary"]),
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents,
                "spacing": "none",
                "paddingAll": "16px",
                "backgroundColor": colors["bg"],
            },
            "footer": self._footer_box(target_url, "查看完整衛教單", colors["primary"]),
        }

        if data.get("image_url"):
            bubble["hero"] = {
                "type": "image",
                "url": data["image_url"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            }

        return bubble

    # ==================================================================
    # 多結果 Carousel
    # ==================================================================
    def _multi_result_carousel(self, results: List[Dict], category: str) -> dict:
        """多筆結果時使用 Carousel 呈現"""
        colors = COLORS.get(category, COLORS["nursing"])
        icon = ICON_MAP.get(category, "📄")

        bubbles = []
        for data in results[:10]:  # Carousel 最多 10 個 Bubble
            target_url = data.get("url") or data.get("link") or "#"
            summary_text = data.get("summary") or data.get("snippet") or data.get("indication", "")
            
            body_items = [
                self._badge(f"{icon} {data.get('category', '查詢結果')}", colors["badge"], colors["badge_text"]),
                {
                    "type": "text",
                    "text": data.get("title", "查詢結果"),
                    "weight": "bold",
                    "size": "md",
                    "color": "#1A1A1A",
                    "wrap": True,
                    "margin": "md",
                },
                {
                    "type": "text",
                    "text": summary_text[:120] if summary_text else "點擊查看詳細內容",
                    "size": "xs",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "sm",
                },
                self._source_text(data.get("source", "EBSCO")),
            ]

            bubble = {
                "type": "bubble",
                "size": "kilo",
                "header": self._header_box(colors["primary"], colors["secondary"]),
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": body_items,
                    "paddingAll": "16px",
                    "backgroundColor": colors["bg"],
                },
                "footer": self._footer_box(target_url, "查看詳細內容", colors["primary"]),
            }

            if data.get("image_url"):
                bubble["hero"] = {
                    "type": "image",
                    "url": data["image_url"],
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                }

            bubbles.append(bubble)

        return {
            "type": "carousel",
            "contents": bubbles,
        }

    # ==================================================================
    # 共用元件
    # ==================================================================
    @staticmethod
    def _header_box(primary_color: str, secondary_color: str) -> dict:
        """頂部裝飾條"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": " ",
                    "size": "xxs",
                }
            ],
            "backgroundColor": primary_color,
            "paddingAll": "4px",
        }

    @staticmethod
    def _badge(text: str, bg_color: str, text_color: str) -> dict:
        """類別標籤"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": text,
                    "size": "xxs",
                    "color": text_color,
                    "weight": "bold",
                }
            ],
            "backgroundColor": bg_color,
            "cornerRadius": "12px",
            "paddingAll": "6px",
            "paddingStart": "10px",
            "paddingEnd": "10px",
            "flex": 0,
        }

    @staticmethod
    def _separator() -> dict:
        """分隔線"""
        return {
            "type": "separator",
            "margin": "lg",
            "color": "#EEEEEE",
        }

    @staticmethod
    def _step_box(step_num: int, title: str, detail: str, color: str) -> dict:
        """步驟方塊"""
        contents = [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": str(step_num),
                                "size": "xs",
                                "color": "#FFFFFF",
                                "weight": "bold",
                                "align": "center",
                            }
                        ],
                        "backgroundColor": color,
                        "cornerRadius": "50px",
                        "flex": 0,
                        "paddingAll": "4px",
                        "paddingStart": "8px",
                        "paddingEnd": "8px",
                        "justifyContent": "center",
                        "alignItems": "center",
                    },
                    {
                        "type": "text",
                        "text": title,
                        "size": "sm",
                        "color": "#333333",
                        "weight": "bold",
                        "margin": "md",
                        "flex": 1,
                        "wrap": True,
                    },
                ],
                "alignItems": "center",
                "margin": "md",
            },
        ]

        if detail:
            contents.append({
                "type": "text",
                "text": detail[:120],
                "size": "xxs",
                "color": "#777777",
                "wrap": True,
                "margin": "sm",
                "offsetStart": "34px",
            })

        return {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "margin": "sm",
        }

    @staticmethod
    def _info_row(label: str, value: str, color: str) -> dict:
        """資訊行（標籤 + 值）"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "xs",
                    "color": color,
                    "weight": "bold",
                    "flex": 0,
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "xs",
                    "color": "#555555",
                    "wrap": True,
                    "flex": 1,
                    "margin": "md",
                },
            ],
            "margin": "md",
            "spacing": "sm",
        }

    @staticmethod
    def _source_text(source: str) -> dict:
        """資料來源標示"""
        return {
            "type": "text",
            "text": f"📚 {source}",
            "size": "xxs",
            "color": "#AAAAAA",
            "margin": "xl",
            "align": "end",
        }

    @staticmethod
    def _footer_box(link: str, label: str, color: str) -> dict:
        """底部按鈕區域"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": label,
                        "uri": link,
                    },
                    "style": "primary",
                    "color": color,
                    "height": "sm",
                }
            ],
            "paddingAll": "12px",
        }
