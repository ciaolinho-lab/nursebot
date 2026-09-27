"""
模擬資料提供者
==============
在尚未取得 EBSCO API 金鑰前，提供豐富的模擬護理資料供開發測試。
資料來源參考公開護理教科書與藥典，僅供示範用途。
"""

from typing import List, Dict
import difflib


class MockDataProvider:
    """模擬資料查詢，介面與 EBSCOClient 完全相同"""

    def __init__(self):
        self._nursing_skills = self._init_nursing_skills()
        self._drugs = self._init_drugs()
        self._diseases = self._init_diseases()
        self._education = self._init_education()

    # ------------------------------------------------------------------
    # 模糊比對搜尋
    # ------------------------------------------------------------------
    def _fuzzy_search(self, keyword: str, data: Dict[str, dict]) -> List[Dict]:
        """根據關鍵字比對資料庫（支援精確、子字串、別名與內文包含）"""
        keyword_lower = keyword.lower().strip()
        if not keyword_lower:
            return []

        results = []
        for key, value in data.items():
            title = value.get("title", "")
            summary = value.get("summary", "")
            generic_name = value.get("generic_name", "")
            brand_names = value.get("brand_names", [])
            aliases = value.get("aliases", [])

            # 精確比對 or 雙向包含
            if (keyword_lower in key.lower() or key.lower() in keyword_lower or
                keyword_lower in title.lower() or
                keyword_lower in summary.lower() or
                keyword_lower in generic_name.lower()):
                results.append(value)
                continue

            # 別名比對
            if any(keyword_lower in alias.lower() or alias.lower() in keyword_lower for alias in aliases):
                results.append(value)
                continue

            # 商品名比對
            if any(keyword_lower in brand.lower() for brand in brand_names):
                results.append(value)
                continue

        # 若上述匹配無結果，嘗試搜尋全文
        if not results:
            import json
            for key, value in data.items():
                content_str = json.dumps(value, ensure_ascii=False).lower()
                if keyword_lower in content_str:
                    results.append(value)

        # 若仍無結果，嘗試相似度比對
        if not results:
            keys = list(data.keys())
            close_matches = difflib.get_close_matches(keyword, keys, n=3, cutoff=0.3)
            for match in close_matches:
                results.append(data[match])

        return results[:5]

    # ------------------------------------------------------------------
    # 公開介面
    # ------------------------------------------------------------------
    def search_all(self, keyword: str) -> Dict[str, List[Dict]]:
        """全庫智慧搜尋，回傳各類別結果字典"""
        results = {}

        nursing_res = self.search_nursing_skill(keyword)
        if nursing_res:
            results["nursing_skill"] = nursing_res

        drug_res = self.search_drug(keyword)
        if drug_res:
            results["drug"] = drug_res

        disease_res = self.search_disease(keyword)
        if disease_res:
            results["disease"] = disease_res

        edu_res = self.search_education(keyword)
        if edu_res:
            results["education"] = edu_res

        return results

    def search_nursing_skill(self, keyword: str) -> List[Dict]:
        if keyword == "ALL_CATEGORY":
            return list(self._nursing_skills.values())[:5]
        return self._fuzzy_search(keyword, self._nursing_skills)

    def search_drug(self, keyword: str) -> List[Dict]:
        if keyword == "ALL_CATEGORY":
            return list(self._drugs.values())[:5]
        return self._fuzzy_search(keyword, self._drugs)

    def search_disease(self, keyword: str) -> List[Dict]:
        if keyword == "ALL_CATEGORY":
            return list(self._diseases.values())[:5]
        return self._fuzzy_search(keyword, self._diseases)

    def search_education(self, keyword: str) -> List[Dict]:
        if keyword == "ALL_CATEGORY":
            return list(self._education.values())[:5]
        return self._fuzzy_search(keyword, self._education)

    # ------------------------------------------------------------------
    # 護理技術操作資料
    # ------------------------------------------------------------------
    @staticmethod
    def _init_nursing_skills() -> Dict[str, dict]:
        return {
            "導尿管置入": {
                "title": "導尿管置入術（Urinary Catheterization）",
                "aliases": ["導尿", "Foley", "foley", "尿管", "留置導尿"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "無菌技術下執行留置導尿管（Foley catheter）置入，適用於急性尿滯留、術前準備及精確尿量監測。",
                "steps": [
                    {"step": 1, "title": "核對醫囑與病人辨識", "detail": "確認醫囑、導尿管型號與尺寸（成人常用 14-16 Fr），執行雙重病人辨識。"},
                    {"step": 2, "title": "準備用物", "detail": "無菌導尿包、手套、潤滑凝膠（含 Lidocaine 為佳）、10 mL 注射器（蒸餾水）、固定貼片、尿袋。"},
                    {"step": 3, "title": "擺位與暴露", "detail": "女性：仰臥屈膝蛙式。男性：仰臥平躺。維護隱私，僅暴露必要區域。"},
                    {"step": 4, "title": "手部衛生與無菌區建立", "detail": "洗手 → 打開無菌包 → 戴無菌手套 → 鋪無菌巾。"},
                    {"step": 5, "title": "消毒會陰", "detail": "以優碘棉球由內而外、由上而下擦拭，每棉球限用一次。女性：分開小陰唇，清潔尿道口。男性：翻開包皮。"},
                    {"step": 6, "title": "插入導尿管", "detail": "潤滑導尿管前端 5-7 cm。女性：插入約 5-7 cm 至尿液流出再推入 2 cm。男性：將陰莖與腹壁呈 60-90° 角，插入約 17-22 cm。"},
                    {"step": 7, "title": "充氣球囊固定", "detail": "確認尿液引流後，注入 10 mL 蒸餾水充氣球囊，輕拉確認固定。"},
                    {"step": 8, "title": "固定與記錄", "detail": "以固定貼片固定於大腿內側（女性）或下腹部（男性），尿袋低於膀胱。記錄尿管型號、插入時間、初始引流量及顏色。"},
                ],
                "warnings": ["嚴格遵守無菌技術", "若遇阻力不可強行推入", "注意乳膠過敏", "定期評估移除時機（CAUTI預防）"],
                "evidence_level": "Level A — 強烈建議",
            },
            "靜脈注射": {
                "title": "周邊靜脈留置針置入（Peripheral IV Insertion）",
                "aliases": ["IV", "打針", "靜脈留置針", "peripheral IV", "輸液"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "建立周邊靜脈通路，用於輸液、給藥與抽血。",
                "steps": [
                    {"step": 1, "title": "核對醫囑與評估", "detail": "確認輸液醫囑、評估病人過敏史、凝血功能，選擇合適留置針號數（常用 18-22 G）。"},
                    {"step": 2, "title": "選擇穿刺部位", "detail": "優先選擇非慣用手前臂遠端靜脈，避開關節處、患側肢體、瘻管側、有傷口或水腫處。"},
                    {"step": 3, "title": "準備用物", "detail": "留置針、透明敷料、延長管、生理食鹽水沖洗注射器、止血帶、酒精棉片、銳器收集盒。"},
                    {"step": 4, "title": "手部衛生與綁止血帶", "detail": "洗手戴手套，於穿刺點上方 10-15 cm 綁止血帶，請病人反覆握拳。"},
                    {"step": 5, "title": "消毒與穿刺", "detail": "以 70% 酒精由中心向外環形消毒，待乾。以 15-30° 角進針，見回血後降低角度再推進 0.2-0.5 cm。"},
                    {"step": 6, "title": "退針芯與固定", "detail": "固定外套管，退出針芯置入銳器盒，連接延長管，以生理食鹽水沖洗確認通暢。"},
                    {"step": 7, "title": "敷料覆蓋與標示", "detail": "以透明敷料覆蓋穿刺點，標示日期、時間、針號。記錄穿刺部位與情形。"},
                ],
                "warnings": ["單次穿刺不超過 2 次嘗試", "留置不超過 72-96 小時", "定期評估穿刺部位（紅腫熱痛）", "注意靜脈炎徵象"],
                "evidence_level": "Level A — 強烈建議",
            },
            "鼻胃管置入": {
                "title": "鼻胃管置入術（Nasogastric Tube Insertion）",
                "aliases": ["NG tube", "NG", "鼻胃管", "nasogastric", "插鼻胃管"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "經鼻腔置入鼻胃管至胃部，用於腸胃減壓、灌食或給藥。",
                "steps": [
                    {"step": 1, "title": "核對醫囑與評估", "detail": "確認醫囑、鼻胃管尺寸（成人常用 14-18 Fr），評估鼻腔通暢度、吞嚥功能、意識狀態。"},
                    {"step": 2, "title": "測量長度", "detail": "從鼻尖→耳垂→劍突（NEX法），以膠帶標記。約 50-65 cm。"},
                    {"step": 3, "title": "擺位", "detail": "半坐臥位（30-45°），下巴微收。準備彎盆、衛生紙、水杯（含吸管）。"},
                    {"step": 4, "title": "潤滑與插入", "detail": "以水溶性潤滑劑潤滑管子前端 10 cm，沿鼻腔底部緩慢推入。達咽喉時（約 10-15 cm）請病人吞嚥配合前進。"},
                    {"step": 5, "title": "確認位置", "detail": "① X光確認（金標準）；② 抽取胃液（pH < 5.5）；③ 聽診法（輔助，非唯一依據）。"},
                    {"step": 6, "title": "固定與記錄", "detail": "以膠帶蝶形固定於鼻翼，記錄外露長度刻度、確認方式、引流液性狀。"},
                ],
                "warnings": ["顱底骨折禁止經鼻插管", "遇阻力時不可強推", "插入過程若持續咳嗽或發紺應立即拔除", "每班確認管路位置"],
                "evidence_level": "Level A — 強烈建議",
            },
            "傷口換藥": {
                "title": "傷口換藥（Wound Dressing Change）",
                "aliases": ["換藥", "wound care", "dressing", "傷口照護"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "依無菌或清潔技術執行傷口換藥，促進傷口癒合並預防感染。",
                "steps": [
                    {"step": 1, "title": "評估傷口", "detail": "評估傷口大小、深度、分泌物、周圍皮膚狀態，記錄 MEASURE 指標或 TIME 框架。"},
                    {"step": 2, "title": "準備用物", "detail": "換藥車、無菌換藥包、合適敷料、生理食鹽水、手套（清潔+無菌）、膠帶、垃圾袋。"},
                    {"step": 3, "title": "移除舊敷料", "detail": "洗手、戴清潔手套。以生理食鹽水濕潤後小心移除，觀察舊敷料上的分泌物性狀。"},
                    {"step": 4, "title": "清潔傷口", "detail": "換戴無菌手套。以生理食鹽水由傷口中心向外環形清潔，每棉球限用一次。"},
                    {"step": 5, "title": "塗藥與覆蓋", "detail": "依醫囑塗抹藥膏或放置適當敷料（如泡棉敷料、人工皮、紗布），由傷口中心向外覆蓋，敷料邊緣需超出傷口 2-3 cm。"},
                    {"step": 6, "title": "固定與記錄", "detail": "以膠帶固定，標記日期時間。記錄傷口評估結果（大小、顏色、滲液量）及使用敷料。"},
                ],
                "warnings": ["注意無菌技術", "評估傷口癒合進程與感染徵象", "選擇合適敷料維持濕潤平衡", "嚴重傷口應照會傷口專科"],
                "evidence_level": "Level B — 建議",
            },
            "抽血": {
                "title": "靜脈抽血（Venipuncture / Blood Specimen Collection）",
                "aliases": ["venipuncture", "blood draw", "採血", "抽血技術"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "以真空採血管系統或空針從周邊靜脈採集血液檢體。",
                "steps": [
                    {"step": 1, "title": "核對醫囑與病人辨識", "detail": "確認檢驗項目、採血管顏色與數量，執行雙重病人辨識，確認空腹要求。"},
                    {"step": 2, "title": "準備用物", "detail": "真空採血管組（holder + 針頭）或 21-23 G 空針、止血帶、酒精棉片、棉球、採血管、標籤。"},
                    {"step": 3, "title": "選擇穿刺部位", "detail": "優先肘前窩（正中肘靜脈 > 頭靜脈 > 貴要靜脈），避開瘻管側、輸液側、患側肢體。"},
                    {"step": 4, "title": "消毒與穿刺", "detail": "綁止血帶（不超過 1 分鐘），以 70% 酒精消毒待乾，15-30° 角進針，見回血後固定。"},
                    {"step": 5, "title": "採集檢體", "detail": "依正確順序接入採血管（血培養→藍→紅→綠→紫→灰），含抗凝劑管輕輕翻轉混勻 8-10 次。"},
                    {"step": 6, "title": "拔針與加壓", "detail": "鬆開止血帶 → 拔針 → 立即以乾棉球加壓 3-5 分鐘（抗凝治療者延長），不可揉搓。"},
                    {"step": 7, "title": "標示與送檢", "detail": "當場於病人面前貼標籤，核對資料，放入檢體袋，依規定時間送檢。"},
                ],
                "warnings": ["止血帶綁紮不超過 1 分鐘", "注意採血管順序", "使用抗凝劑者延長加壓時間", "針扎預防：單手回套或直接丟棄銳器盒"],
                "evidence_level": "Level A — 強烈建議",
            },
            "氧氣治療": {
                "title": "氧氣治療（Oxygen Therapy）",
                "aliases": ["O2", "oxygen", "給氧", "氧氣面罩", "鼻導管"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "依醫囑提供適當濃度之氧氣，矯正低血氧症，維持 SpO₂ ≥ 94%（COPD 患者 88-92%）。",
                "steps": [
                    {"step": 1, "title": "評估與核對醫囑", "detail": "評估呼吸狀態、SpO₂、意識、發紺。確認醫囑氧氣流量與裝置類型。"},
                    {"step": 2, "title": "選擇給氧裝置", "detail": "鼻導管（1-6 L/min, 24-44%）、簡單面罩（5-8 L/min, 40-60%）、非再吸入面罩（10-15 L/min, 80-100%）、Venturi 面罩（精確 FiO₂）。"},
                    {"step": 3, "title": "設備連接", "detail": "連接氧氣流量表至氣源，接上潮濕瓶（流量 > 4 L/min 時），調整至醫囑流量，確認有氣流。"},
                    {"step": 4, "title": "裝置病人", "detail": "協助病人戴上裝置，調整鬆緊度確保舒適。鼻導管固定於耳後，面罩需密合。"},
                    {"step": 5, "title": "持續監測", "detail": "每 1-2 小時監測 SpO₂、呼吸型態、意識變化，評估皮膚壓損（鼻翼、耳後）。"},
                ],
                "warnings": ["COPD 患者避免高流量氧氣（目標 SpO₂ 88-92%）", "氧氣設備周圍禁止火源", "長期高濃度氧氣可致氧中毒", "定期更換潮濕瓶"],
                "evidence_level": "Level A — 強烈建議",
            },
            "生命徵象測量": {
                "title": "生命徵象測量（Vital Signs Measurement）",
                "aliases": ["vital signs", "VS", "TPR", "血壓", "體溫", "脈搏", "呼吸"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "系統性測量體溫、脈搏、呼吸、血壓，評估病人生理狀態。",
                "steps": [
                    {"step": 1, "title": "準備與評估", "detail": "確認病人休息至少 5 分鐘、未進食、未運動。準備體溫計、血壓計、聽診器、手錶。"},
                    {"step": 2, "title": "體溫測量", "detail": "口溫（36.0-37.5°C）、腋溫（35.5-37.0°C）、耳溫（35.8-37.8°C）、額溫。選擇合適部位與方法。"},
                    {"step": 3, "title": "脈搏測量", "detail": "觸摸橈動脈，計數 60 秒（不規則時）或 30 秒 ×2。正常成人 60-100 次/分。評估速率、節律、強度。"},
                    {"step": 4, "title": "呼吸測量", "detail": "不告知病人下計數呼吸次數 60 秒。正常成人 12-20 次/分。觀察深度、節律、型態。"},
                    {"step": 5, "title": "血壓測量", "detail": "壓脈帶寬度為上臂圍 40%，下緣距肘窩 2-3 cm。先觸診收縮壓，再聽診法測量。正常 < 120/80 mmHg。"},
                    {"step": 6, "title": "記錄與通報", "detail": "完整記錄於生命徵象紀錄表，異常值立即通報醫師並啟動相應處置。"},
                ],
                "warnings": ["雙側測量第一次（差距 > 10 mmHg 需追蹤）", "壓脈帶大小影響準確度", "發燒時同步評估其他感染徵象", "使用 NEWS/MEWS 評分系統"],
                "evidence_level": "Level A — 強烈建議",
            },
            "給藥技術": {
                "title": "藥物給予（Medication Administration）",
                "aliases": ["給藥", "medication", "三讀五對", "用藥安全"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "依醫囑正確、安全地給予藥物，執行三讀五對確保用藥安全。",
                "steps": [
                    {"step": 1, "title": "三讀五對", "detail": "三讀：取藥時、備藥時、給藥前核對藥物。五對：對病人、對藥物、對劑量、對途徑、對時間。"},
                    {"step": 2, "title": "評估病人", "detail": "確認過敏史、用藥史、意識狀態、吞嚥功能，評估給藥途徑的適當性。"},
                    {"step": 3, "title": "準備藥物", "detail": "確認藥物外觀、有效期限、儲存條件。必要時磨粉或稀釋（確認可否磨粉）。"},
                    {"step": 4, "title": "給予藥物", "detail": "病人辨識後給予藥物，確認病人確實服下。IV push 注意給藥速度，IM 選擇正確注射部位。"},
                    {"step": 5, "title": "監測與記錄", "detail": "觀察藥物反應（療效與副作用），記錄給藥時間、劑量、途徑、病人反應。"},
                ],
                "warnings": ["高警訊藥物需雙人核對", "嚴禁口頭醫囑（緊急除外）", "若對醫囑有疑慮應先確認再給藥", "注意藥物交互作用"],
                "evidence_level": "Level A — 強烈建議",
            },
            "CPR": {
                "title": "心肺復甦術（Cardiopulmonary Resuscitation, CPR）",
                "aliases": ["心肺復甦", "急救", "ACLS", "BLS", "cardiac arrest"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "針對心跳停止病人執行高品質 CPR，遵循 AHA 最新指引 C-A-B 流程。",
                "steps": [
                    {"step": 1, "title": "辨識與啟動", "detail": "評估反應與呼吸（≤ 10 秒），無反應無正常呼吸 → 呼叫支援、啟動 Code Blue、取得 AED/除顫器。"},
                    {"step": 2, "title": "胸外按壓 (C)", "detail": "雙手交叉掌根置於胸骨下半段，按壓深度 5-6 cm，速率 100-120 次/分，確保完全回彈，減少中斷。"},
                    {"step": 3, "title": "暢通呼吸道 (A)", "detail": "壓額抬下巴法（無頸椎損傷疑慮）或推下顎法，清除口腔異物。"},
                    {"step": 4, "title": "人工呼吸 (B)", "detail": "以 BVM 給予通氣，每次 1 秒鐘，可見胸廓起伏。壓胸：通氣 = 30:2（未建立進階呼吸道前）。"},
                    {"step": 5, "title": "使用 AED/除顫", "detail": "貼上電極貼片，依機器指示操作。可電擊心律 → 電擊 → 立即恢復按壓 2 分鐘。不可電擊心律 → 持續 CPR。"},
                    {"step": 6, "title": "進階處置", "detail": "建立靜脈通路、給予 Epinephrine（每 3-5 分鐘）、考慮進階呼吸道、找出可逆原因（5H5T）。"},
                ],
                "warnings": ["每 2 分鐘更換按壓者", "按壓中斷不超過 10 秒", "確保按壓品質（足夠深度與完全回彈）", "團隊溝通使用閉環溝通"],
                "evidence_level": "Level A — 強烈建議（AHA 2025 Guidelines）",
            },
            "血糖監測": {
                "title": "指尖血糖監測（Capillary Blood Glucose Monitoring）",
                "aliases": ["blood sugar", "glucose", "POCT", "指尖血糖", "血糖機"],
                "source": "Gemini 護理 AI 助手",
                "url": "https://gemini.google.com/app",
                "link": "https://gemini.google.com/app",
                "summary": "以攜帶型血糖機測量指尖毛細血管血糖值，用於糖尿病患者血糖管理。",
                "steps": [
                    {"step": 1, "title": "核對與準備", "detail": "確認醫囑頻率與時機（AC/PC/HS），準備血糖機、試紙、採血針、酒精棉片、棉球。確認試紙校正碼。"},
                    {"step": 2, "title": "選擇穿刺部位", "detail": "選擇指腹側面（無名指或中指優先），避免拇指與食指。確認手指溫暖、無水腫。"},
                    {"step": 3, "title": "消毒與穿刺", "detail": "以酒精消毒待完全乾燥，使用採血針穿刺，擠壓出足量血滴。棄除第一滴血（依機型而定）。"},
                    {"step": 4, "title": "測量與記錄", "detail": "將血液接觸試紙吸血端，等待機器讀數。正常空腹值 70-110 mg/dL。記錄數值、時間、餐前/後。"},
                    {"step": 5, "title": "處置與通報", "detail": "< 70 mg/dL：低血糖處理（15-15法則）。> 300 mg/dL：通知醫師並依醫囑處置。"},
                ],
                "warnings": ["試紙需在有效期限內", "酒精需完全乾燥再穿刺（避免溶血影響結果）", "注意不同血糖機的誤差範圍", "嚴重貧血或脫水可能影響準確度"],
                "evidence_level": "Level A — 強烈建議",
            },
        }

    # ------------------------------------------------------------------
    # 藥物資料
    # ------------------------------------------------------------------
    @staticmethod
    def _init_drugs() -> Dict[str, dict]:
        return {
            "Acetaminophen": {
                "title": "Acetaminophen（乙醯氨酚 / 普拿疼）",
                "aliases": ["acetaminophen", "Panadol", "panadol", "普拿疼", "乙醯氨酚", "Tylenol", "tylenol", "退燒藥", "止痛藥"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/acetaminophen",
                "generic_name": "Acetaminophen / Paracetamol",
                "brand_names": ["Panadol", "Tylenol", "Scanol"],
                "drug_class": "乙醯氨酚類解熱鎮痛劑（Analgesic / Antipyretic）",
                "indication": "輕中度疼痛（頭痛、牙痛、肌肉痛）、發燒。",
                "mechanism": "主要作用於中樞神經系統，抑制前列腺素合成，達到解熱鎮痛效果。",
                "dosage": "成人每次 500 mg q4-6h，每日最大劑量不超過 4000 mg（肝功能不全者減量）。",
                "side_effects": ["肝毒性（超量使用）", "過敏反應（皮疹）", "腎功能損傷（長期大劑量）"],
                "contraindications": ["嚴重肝功能不全或活動性肝病", "對本藥成分過敏"],
                "nursing_considerations": [
                    "確認 24 小時內總劑量不可超過 4000 mg",
                    "注意複方感冒藥中是否含有 Acetaminophen 避免重複給藥",
                    "長期酗酒或肝病患者需減量",
                    "解毒劑：N-acetylcysteine (NAC)",
                ],
            },
            "Aspirin": {
                "title": "Aspirin（阿斯匹靈 / 伯基）",
                "aliases": ["aspirin", "Bokey", "bokey", "阿斯匹靈", "伯基", "阿司匹林", "ASA"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/aspirin",
                "generic_name": "Acetylsalicylic Acid (ASA)",
                "brand_names": ["Bokey", "Aspirin Protect", "Tapal"],
                "drug_class": "抗血小板劑 / 水楊酸類（Antiplatelet / NSAID）",
                "indication": "急性心肌梗塞、缺血性中風、二級中風與心血管事件預防。",
                "mechanism": "不可逆抑制環氧合酶-1 (COX-1)，減少血栓素 A2 (TXA2) 形成，抑制血小板凝集。",
                "dosage": "抗血小板預防：75-100 mg QD；急性心肌梗塞：162-325 mg 咬碎服下。",
                "side_effects": ["腸胃道出血 / 潰瘍", "瘀青、出血時間延長", "阿斯匹靈誘發之氣喘"],
                "contraindications": ["消化性潰瘍活動期", "血友病或凝血功能障礙", "水楊酸過敏", "18 歲以下水痘/流感患者（Reye症候群）"],
                "nursing_considerations": [
                    "衛教飯後服用或使用腸溶錠以減少胃部刺激",
                    "監測出血徵象（黑便、血尿、牙齦出血）",
                    "手術前 5-7 天依醫囑評估是否停藥",
                    "注意 Reye 症候群風險",
                ],
            },
            "Metformin": {
                "title": "Metformin（美福明 / 二甲雙胍）",
                "aliases": ["metformin", "Glucophage", "glucophage", "美福明", "二甲雙胍"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/metformin",
                "generic_name": "Metformin Hydrochloride",
                "brand_names": ["Glucophage", "Glucophage XR", "Fortamet"],
                "drug_class": "雙胍類降血糖藥（Biguanides）",
                "indication": "第二型糖尿病之一線藥物治療",
                "mechanism": "抑制肝臟糖質新生、增加周邊組織對胰島素敏感性、減少腸道葡萄糖吸收。",
                "dosage": "起始 500 mg BID 或 850 mg QD，漸增至最大 2550 mg/day，隨餐服用。",
                "side_effects": ["腸胃不適（噁心、腹瀉、腹脹）", "乳酸酸中毒（罕見但致命）", "維生素 B12 缺乏（長期使用）"],
                "contraindications": ["嚴重腎功能不全（eGFR < 30）", "急性代謝性酸中毒", "使用含碘顯影劑前後 48 小時"],
                "nursing_considerations": [
                    "定期監測腎功能（eGFR）",
                    "衛教隨餐服用以減少腸胃副作用",
                    "長期使用者檢測 Vitamin B12",
                    "手術或使用顯影劑前需暫停",
                ],
            },
            "Insulin": {
                "title": "Insulin（胰島素）",
                "aliases": ["insulin", "胰島素", "RI", "Lantus", "NovoRapid", "Humulin"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/insulin",
                "generic_name": "Insulin (various formulations)",
                "brand_names": ["NovoRapid", "Humalog", "Lantus", "Levemir", "Humulin R"],
                "drug_class": "胰島素製劑（Insulin Preparations）",
                "indication": "第一型糖尿病、第二型糖尿病血糖控制不佳、糖尿病酮酸血症、高血糖急症。",
                "mechanism": "促進葡萄糖進入細胞、抑制肝臟糖質新生、促進脂肪與蛋白質合成。",
                "dosage": "依病人血糖控制目標個別化調整。速效：飯前 15 分鐘；長效：固定時間每日一次。",
                "side_effects": ["低血糖（最常見且最危險）", "注射部位脂肪萎縮", "體重增加", "過敏反應（罕見）"],
                "contraindications": ["低血糖發作時", "對該胰島素成分過敏"],
                "nursing_considerations": [
                    "儲存：未開封冰箱 2-8°C，開封後室溫 28 天",
                    "注射部位輪替（腹部吸收最快）",
                    "混合胰島素時：先抽清（RI）後抽濁（NPH）",
                    "監測血糖，衛教低血糖症狀與處理（15-15法則）",
                    "高警訊藥物：需雙人核對",
                ],
            },
            "Warfarin": {
                "title": "Warfarin（華法林 / 可邁丁）",
                "aliases": ["warfarin", "Coumadin", "coumadin", "華法林", "可邁丁"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/warfarin",
                "generic_name": "Warfarin Sodium",
                "brand_names": ["Coumadin", "Jantoven"],
                "drug_class": "維生素 K 拮抗劑（Vitamin K Antagonist）",
                "indication": "深層靜脈血栓（DVT）、肺栓塞（PE）、心房顫動合併中風預防、機械瓣膜。",
                "mechanism": "抑制維生素 K 依賴性凝血因子（II、VII、IX、X）及蛋白 C、S 的合成。",
                "dosage": "起始 2-5 mg QD，依 INR 調整。目標 INR 通常 2.0-3.0（機械瓣膜 2.5-3.5）。",
                "side_effects": ["出血（最常見）", "皮膚壞死（罕見）", "紫趾症候群", "藥物交互作用眾多"],
                "contraindications": ["活動性出血", "嚴重肝病", "懷孕（致畸胎）", "近期 CNS 手術"],
                "nursing_considerations": [
                    "定期監測 INR（目標 2.0-3.0）",
                    "衛教避免攝取不穩定量的維生素 K 食物",
                    "注意出血徵象（牙齦出血、血尿、黑便、瘀青）",
                    "避免與 NSAIDs 併用",
                    "解毒劑：Vitamin K₁（Phytonadione）",
                    "高警訊藥物：需雙人核對",
                ],
            },
            "Heparin": {
                "title": "Heparin（肝素）",
                "aliases": ["heparin", "UFH", "肝素", "抗凝"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/heparin",
                "generic_name": "Heparin Sodium (Unfractionated)",
                "brand_names": ["Heparin Sodium Injection"],
                "drug_class": "抗凝血劑（Anticoagulant）",
                "indication": "DVT/PE 治療與預防、ACS、心臟手術體外循環、DIC。",
                "mechanism": "增強 Antithrombin III 活性，抑制凝血因子 IIa (Thrombin)、Xa 等。",
                "dosage": "DVT/PE：Bolus 80 U/kg → 18 U/kg/hr 持續滴注，依 aPTT 調整。預防劑量：5000 U SC q8-12h。",
                "side_effects": ["出血", "HIT（肝素誘導性血小板低下症）", "骨質疏鬆（長期使用）", "注射部位瘀青"],
                "contraindications": ["HIT 病史", "活動性出血", "嚴重血小板低下"],
                "nursing_considerations": [
                    "監測 aPTT（目標 1.5-2.5 倍正常值）",
                    "定期追蹤血小板計數（HIT 偵測）",
                    "解毒劑：Protamine Sulfate",
                    "IV 使用 infusion pump 精確控制速度",
                    "高警訊藥物：需雙人核對",
                    "不可 IM 注射",
                ],
            },
            "Digoxin": {
                "title": "Digoxin（地高辛 / 毛地黃）",
                "aliases": ["digoxin", "Lanoxin", "毛地黃", "地高辛"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/digoxin",
                "generic_name": "Digoxin",
                "brand_names": ["Lanoxin"],
                "drug_class": "強心配醣體（Cardiac Glycoside）",
                "indication": "心衰竭（HFrEF）、心房顫動/心房撲動之心室速率控制。",
                "mechanism": "抑制 Na⁺/K⁺-ATPase → 增加細胞內 Ca²⁺ → 正性肌力作用。副交感神經增強 → 減慢房室傳導。",
                "dosage": "口服：0.125-0.25 mg QD。老年人或腎功能不全者減量。治療血中濃度 0.5-2.0 ng/mL。",
                "side_effects": ["毛地黃中毒（噁心、嘔吐、視覺異常-黃綠色光暈、心律不整）", "心搏過緩", "電解質異常"],
                "contraindications": ["肥厚性阻塞型心肌病", "嚴重竇性病變", "低血鉀（增加毒性風險）"],
                "nursing_considerations": [
                    "給藥前測量心尖脈 1 分鐘（< 60 bpm 暫停給藥並通知醫師）",
                    "監測 Digoxin 血中濃度（治療範圍 0.5-2.0 ng/mL）",
                    "監測鉀離子（低鉀增加毛地黃毒性）",
                    "解毒劑：Digoxin Immune Fab (Digibind)",
                    "衛教辨識毒性症狀",
                    "高警訊藥物：需雙人核對",
                ],
            },
            "Amlodipine": {
                "title": "Amlodipine（氨氯地平 / 脈優）",
                "aliases": ["amlodipine", "Norvasc", "脈優", "氨氯地平"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/amlodipine",
                "generic_name": "Amlodipine Besylate",
                "brand_names": ["Norvasc"],
                "drug_class": "鈣離子通道阻斷劑（Calcium Channel Blocker, DHP type）",
                "indication": "高血壓、穩定型心絞痛、血管痙攣型心絞痛。",
                "mechanism": "阻斷 L-type 鈣離子通道，減少血管平滑肌鈣離子流入，擴張周邊動脈，降低血壓。",
                "dosage": "起始 5 mg QD，可調至 10 mg QD。老年人起始 2.5 mg。",
                "side_effects": ["周邊水腫（踝部）", "頭痛", "臉潮紅", "頭暈", "心悸"],
                "contraindications": ["嚴重主動脈狹窄", "對本藥成分過敏"],
                "nursing_considerations": [
                    "定期監測血壓",
                    "衛教可能出現踝部水腫（與劑量相關）",
                    "不可突然停藥",
                    "葡萄柚汁可能增加藥物濃度",
                ],
            },
            "Enoxaparin": {
                "title": "Enoxaparin（依諾肝素）",
                "aliases": ["enoxaparin", "Clexane", "LMWH", "低分子量肝素", "依諾肝素"],
                "source": "DynaMed — Drug Information",
                "link": "https://www.dynamed.com/drug-monograph/enoxaparin",
                "generic_name": "Enoxaparin Sodium",
                "brand_names": ["Clexane", "Lovenox"],
                "drug_class": "低分子量肝素（Low Molecular Weight Heparin）",
                "indication": "DVT/PE 治療與預防、ACS、骨科術後血栓預防。",
                "mechanism": "主要抑制 Factor Xa（Xa:IIa 約 3.8:1），較 UFH 有更可預測的藥物動力學。",
                "dosage": "治療：1 mg/kg SC q12h 或 1.5 mg/kg SC QD。預防：40 mg SC QD。腎功能不全需調整。",
                "side_effects": ["出血", "注射部位瘀血/血腫", "HIT（較 UFH 少見）", "高血鉀（少見）"],
                "contraindications": ["HIT 病史", "活動性出血", "嚴重腎功能不全需調整劑量"],
                "nursing_considerations": [
                    "SC 注射於腹壁（距肚臍 5 cm），不可排出氣泡",
                    "不需常規監測 aPTT（必要時測 Anti-Xa level）",
                    "腎功能不全者（CrCl < 30）需減量",
                    "注射後不可揉搓注射部位",
                    "術前 12-24 小時停用",
                ],
            },
        }

    # ------------------------------------------------------------------
    # 疾病照護指引
    # ------------------------------------------------------------------
    @staticmethod
    def _init_diseases() -> Dict[str, dict]:
        return {
            "糖尿病": {
                "title": "第二型糖尿病照護指引（Type 2 Diabetes Management）",
                "aliases": ["DM", "diabetes", "T2DM", "type 2 diabetes", "血糖"],
                "source": "Cochrane Library 實證醫學資料庫",
                "link": "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=Diabetes+Mellitus",
                "summary": "第二型糖尿病是以胰島素阻抗為主的慢性代謝疾病，需多面向管理。",
                "key_points": [
                    "診斷標準：HbA1c ≥ 6.5%、空腹血糖 ≥ 126 mg/dL、OGTT 2h ≥ 200 mg/dL",
                    "一線藥物：Metformin（無禁忌症時）",
                    "HbA1c 目標：一般 < 7%，老年人可放寬至 < 8%",
                    "合併 ASCVD 或 CKD：優先考慮 SGLT2i 或 GLP-1 RA",
                    "每年篩檢併發症：眼底、腎功能、足部、神經病變",
                ],
                "nursing_focus": [
                    "血糖監測與紀錄",
                    "胰島素注射技術指導",
                    "低血糖辨識與處理衛教（15-15法則）",
                    "足部護理評估與衛教",
                    "飲食與運動諮詢轉介",
                    "就醫遵從性評估",
                ],
            },
            "高血壓": {
                "title": "高血壓照護指引（Hypertension Management）",
                "aliases": ["HTN", "hypertension", "血壓高"],
                "source": "Cochrane Library 實證醫學資料庫",
                "link": "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=Hypertension",
                "summary": "高血壓為最常見的心血管危險因子，適當控制可顯著降低中風、心衰竭及腎病風險。",
                "key_points": [
                    "診斷：診間血壓 ≥ 140/90 mmHg（至少 2 次不同日測量確認）",
                    "目標：一般 < 130/80 mmHg；老年人可放寬至 < 140/90 mmHg",
                    "一線藥物：ACEi/ARB、CCB、Thiazide 利尿劑",
                    "非藥物治療：DASH 飲食、減鈉 < 2.3 g/day、規律運動、減重、限酒",
                    "高血壓危象：SBP > 180 或 DBP > 120 → 評估是否有靶器官損傷",
                ],
                "nursing_focus": [
                    "正確測量血壓技術",
                    "衛教規律服藥的重要性",
                    "監測藥物副作用（頭暈、電解質異常）",
                    "生活型態調整指導",
                    "居家血壓監測指導",
                    "高血壓危象的辨識與緊急處置",
                ],
            },
            "肺炎": {
                "title": "社區型肺炎照護指引（Community-Acquired Pneumonia）",
                "aliases": ["pneumonia", "CAP", "肺部感染"],
                "source": "Cochrane Library 實證醫學資料庫",
                "link": "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=Pneumonia",
                "summary": "社區型肺炎為常見且具潛在致命性的下呼吸道感染，需早期辨識與適當抗生素治療。",
                "key_points": [
                    "常見病原體：S. pneumoniae、H. influenzae、M. pneumoniae、呼吸道病毒",
                    "嚴重度評估：CURB-65 或 PSI/PORT 評分",
                    "輕度（門診）：Amoxicillin 或 Doxycycline",
                    "中度（住院）：β-lactam + Macrolide 或呼吸道 Fluoroquinolone",
                    "重度（ICU）：β-lactam + Macrolide/Fluoroquinolone，考慮 MRSA/Pseudomonas 涵蓋",
                ],
                "nursing_focus": [
                    "呼吸狀態持續監測（SpO₂、呼吸型態）",
                    "痰液收集與送檢（抗生素前採集）",
                    "氧氣治療管理",
                    "翻身拍背、肺部物理治療",
                    "營養與水分補充評估",
                    "隔離防護措施（必要時）",
                    "出院衛教：肺炎鏈球菌疫苗接種",
                ],
            },
            "心衰竭": {
                "title": "心衰竭照護指引（Heart Failure Management）",
                "aliases": ["HF", "CHF", "heart failure", "心臟衰竭"],
                "source": "Cochrane Library 實證醫學資料庫",
                "link": "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=Heart+Failure",
                "summary": "心衰竭為心臟無法提供足夠血液滿足身體代謝需求之臨床症候群，需終身管理。",
                "key_points": [
                    "分類：HFrEF（EF ≤ 40%）、HFmrEF（41-49%）、HFpEF（≥ 50%）",
                    "NYHA 分級：I-IV 級評估活動耐受度",
                    "HFrEF 四大基石藥物：ACEi/ARB/ARNI + β-blocker + MRA + SGLT2i",
                    "容量管理：限鈉（< 2 g/day）、限水（嚴重時 < 1.5 L/day）",
                    "裝置治療：ICD（預防猝死）、CRT（同步化治療）",
                ],
                "nursing_focus": [
                    "每日量體重（同時間、同衣物、同磅秤）",
                    "體重增加 > 1 kg/天 或 > 2 kg/週需通報",
                    "I/O 監測與水分限制執行",
                    "活動耐受度評估與分級活動指導",
                    "低鈉飲食衛教",
                    "用藥遵從性監測（特別是利尿劑、ACEi）",
                    "出院準備：自我照護能力評估",
                ],
            },
            "中風": {
                "title": "急性缺血性中風照護（Acute Ischemic Stroke）",
                "aliases": ["stroke", "CVA", "腦中風", "缺血性中風"],
                "source": "Cochrane Library 實證醫學資料庫",
                "link": "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=Stroke",
                "summary": "急性缺血性中風為腦血管阻塞導致腦組織缺血壞死，時間即大腦（Time is Brain）。",
                "key_points": [
                    "辨識：FAST（Face-Arm-Speech-Time）",
                    "影像學：CT 排除出血 → 考慮 CT Angiography",
                    "血栓溶解：發作 4.5 小時內 IV tPA (Alteplase)",
                    "取栓手術：大血管阻塞 24 小時內機械取栓",
                    "二級預防：抗血小板、Statin、控制危險因子",
                ],
                "nursing_focus": [
                    "到院即啟動中風團隊（Code Stroke）",
                    "NIHSS 評估與持續神經學監測",
                    "tPA 輸注中密切監測出血徵象",
                    "吞嚥評估（NPO until screened）",
                    "預防併發症：DVT、壓瘡、吸入性肺炎",
                    "早期復健介入與轉介",
                    "心理社會支持與家屬衛教",
                ],
            },
        }

    # ------------------------------------------------------------------
    # 衛教單張
    # ------------------------------------------------------------------
    @staticmethod
    def _init_education() -> Dict[str, dict]:
        return {
            "傷口照護": {
                "title": "傷口居家照護衛教單",
                "aliases": ["wound care", "傷口", "換藥"],
                "source": "照護線上 CareOnline",
                "link": "https://www.careonline.com.tw/p/topic-wound.html?utm_source=gemini",
                "target_audience": "病人與家屬",
                "content": [
                    {"section": "傷口清潔", "points": ["每日以生理食鹽水輕柔清洗", "由傷口中心向外清潔", "避免使用雙氧水或酒精直接沖洗傷口"]},
                    {"section": "換藥方法", "points": ["洗手後戴清潔手套", "移除舊敷料觀察傷口情形", "覆蓋清潔敷料並固定"]},
                    {"section": "觀察重點", "points": ["紅腫熱痛加劇", "異常分泌物（黃綠色、惡臭）", "發燒 > 38°C"]},
                    {"section": "何時就醫", "points": ["傷口持續出血無法止住", "傷口裂開或異物嵌入", "出現感染徵象超過 2 天未改善"]},
                ],
            },
            "糖尿病飲食": {
                "title": "糖尿病飲食衛教單",
                "aliases": ["diabetic diet", "DM diet", "糖尿病飲食控制", "血糖飲食"],
                "source": "照護線上 CareOnline",
                "link": "https://www.careonline.com.tw/?s=%E7%B3%96%E5%B0%BF%E7%97%85&utm_source=gemini",
                "target_audience": "糖尿病病人與家屬",
                "content": [
                    {"section": "六大類食物均衡", "points": ["全穀雜糧類控制份量", "蛋白質選擇豆魚蛋肉類", "蔬菜每餐至少 1 碗", "水果每日 2 份為限"]},
                    {"section": "醣類計算", "points": ["認識 1 份醣類 = 15 克碳水化合物", "澱粉、水果、乳品都含醣", "學會看營養標示"]},
                    {"section": "飲食原則", "points": ["定時定量不跳餐", "避免精緻糖與含糖飲料", "增加纖維攝取", "使用健康烹調方式"]},
                    {"section": "外食建議", "points": ["選擇清蒸、滷、烤取代油炸", "醬料另外放", "自助餐可控制份量"]},
                ],
            },
            "跌倒預防": {
                "title": "住院病人跌倒預防衛教單",
                "aliases": ["fall prevention", "跌倒", "防跌"],
                "source": "照護線上 CareOnline",
                "link": "https://www.careonline.com.tw/2022/06/osteoporosis.html?utm_source=gemini",
                "target_audience": "住院病人與家屬",
                "content": [
                    {"section": "環境安全", "points": ["保持走道淨空", "使用床欄（兩側上升）", "夜間小燈照明", "浴室使用防滑墊"]},
                    {"section": "活動安全", "points": ["下床前先坐起 1 分鐘", "使用合適的助行器或拐杖", "穿著防滑鞋/拖鞋", "如需協助請按鈴呼叫"]},
                    {"section": "藥物注意", "points": ["服用安眠藥/鎮靜劑後臥床休息", "降血壓藥可能造成姿態性低血壓", "使用利尿劑需注意頻尿"]},
                    {"section": "高危險群辨識", "points": ["65 歲以上", "曾有跌倒經驗", "使用助行器或拐杖", "服用多種藥物"]},
                ],
            },
            "壓瘡預防": {
                "title": "壓瘡（壓力性損傷）預防衛教單",
                "aliases": ["pressure injury", "pressure ulcer", "褥瘡", "壓瘡"],
                "source": "照護線上 CareOnline",
                "link": "https://www.careonline.com.tw/?s=%E5%A3%93%E7%99%AE&utm_source=gemini",
                "target_audience": "長期臥床病人與家屬照顧者",
                "content": [
                    {"section": "什麼是壓瘡", "points": ["長時間壓迫導致皮膚及組織損傷", "好發部位：薦骨、足跟、髖骨、肩胛骨", "分為 1-4 期"]},
                    {"section": "預防措施", "points": ["每 2 小時翻身一次", "使用減壓床墊", "保持皮膚清潔乾燥", "避免拖拉移動病人"]},
                    {"section": "營養補充", "points": ["攝取足夠蛋白質與熱量", "補充維生素 C 與鋅", "維持足夠水分攝取"]},
                    {"section": "皮膚檢查", "points": ["每日檢查受壓部位皮膚", "注意發紅、破皮、水泡", "發現異常立即通報護理師"]},
                ],
            },
            "手術前準備": {
                "title": "手術前準備衛教單",
                "aliases": ["preoperative", "手術準備", "pre-op", "術前"],
                "source": "照護線上 CareOnline",
                "link": "https://www.careonline.com.tw/?s=%E6%89%8B%E8%A1%93&utm_source=gemini",
                "target_audience": "手術病人與家屬",
                "content": [
                    {"section": "手術前一天", "points": ["依指示完成術前檢查（抽血、X光、心電圖）", "洗澡清潔身體", "移除指甲油、飾品、假牙、隱形眼鏡", "確認手術同意書已簽署"]},
                    {"section": "禁食規定", "points": ["一般術前禁食 8 小時（固體食物）", "清澈液體可於術前 2 小時前飲用", "依麻醉醫師指示為準"]},
                    {"section": "藥物調整", "points": ["抗凝血劑需依醫囑停用", "降血糖藥/胰島素可能需調整", "高血壓藥通常照常服用（少量水送服）", "主動告知所有使用中的藥物"]},
                    {"section": "心理準備", "points": ["了解手術方式與預期恢復過程", "術後疼痛評估與控制方式", "練習深呼吸及咳嗽技巧", "有任何疑問請隨時詢問醫護團隊"]},
                ],
            },
        }
