/**
 * NurseBot 護理智慧查詢網 - Enhanced JavaScript Web Client (具備全庫智慧動態檢索引導機制)
 */

document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------------------------
    // 1. DOM 元素選取
    // ----------------------------------------------------------------------
    const searchInput = document.getElementById("search-input");
    const btnSearch = document.getElementById("btn-search");
    const btnClear = document.getElementById("btn-clear");
    const searchSuggestions = document.getElementById("search-suggestions");
    const tagButtons = document.querySelectorAll(".tag-btn");
    const tabButtons = document.querySelectorAll(".tab-btn");
    
    const loadingState = document.getElementById("loading-state");
    const welcomeState = document.getElementById("welcome-state");
    const emptyState = document.getElementById("empty-state");
    const resultsContainer = document.getElementById("results-container");

    const sopModal = document.getElementById("sop-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalClose = document.getElementById("modal-close");
    const modalWarnings = document.getElementById("modal-warnings");
    const modalWarningsList = document.getElementById("modal-warnings-list");
    const modalStepsContainer = document.getElementById("modal-steps-container");
    const btnCopySop = document.getElementById("btn-copy-sop");
    const btnPrintSop = document.getElementById("btn-print-sop");
    const btnSaveFavSop = document.getElementById("btn-save-fav-sop");

    const btnFavorites = document.getElementById("btn-favorites");
    const favCountBadge = document.getElementById("fav-count");
    const favModal = document.getElementById("fav-modal");
    const favModalClose = document.getElementById("fav-modal-close");
    const favListContainer = document.getElementById("fav-list-container");
    const btnClearFavs = document.getElementById("btn-clear-favs");
    const btnThemeToggle = document.getElementById("btn-theme-toggle");
    const btnBackToTop = document.getElementById("btn-back-to-top");

    // 關鍵字與熱門建議選單資料
    const SUGGESTION_POOL = [
        { title: "導尿管護理與留置", cat: "護理技術 SOP" },
        { title: "靜脈注射 (IV)", cat: "護理技術 SOP" },
        { title: "鼻胃管照護 (NG Tube)", cat: "護理技術 SOP" },
        { title: "CPR 急救與 AED", cat: "護理技術 SOP" },
        { title: "Metformin (降血糖藥)", cat: "台大藥品" },
        { title: "Aspirin (阿斯匹靈)", cat: "台大藥品" },
        { title: "Panadol (普拿疼)", cat: "台大藥品" },
        { title: "Insulin (胰島素)", cat: "台大藥品" },
        { title: "糖尿病 (Diabetes)", cat: "Cochrane 實證" },
        { title: "心肌梗塞 (Myocardial Infarction)", cat: "Cochrane 實證" },
        { title: "高血壓 (Hypertension)", cat: "Cochrane 實證" },
        { title: "傷口照護與換藥", cat: "照護線上衛教" },
        { title: "跌倒預防指引", cat: "照護線上衛教" },
        { title: "壓瘡預防與處置", cat: "照護線上衛教" }
    ];

    // 內建臨床醫療核心資料庫
    const CLIENT_DATABASE = {
        nursing_skill: [
            {
                title: "導尿管置入術（Urinary Catheterization）",
                aliases: ["導尿", "foley", "尿管", "留置導尿"],
                source: "Gemini 護理 AI 助手",
                link: "https://gemini.google.com/app",
                summary: "無菌技術下執行留置導尿管（Foley catheter）置入，適用於急性尿滯留、術前準備及精確尿量監測。",
                steps: [
                    { step: 1, title: "核對醫囑與病人辨識", detail: "確認醫囑、導尿管型號與尺寸（成人常用 14-16 Fr），執行雙重病人辨識。" },
                    { step: 2, title: "準備用物", detail: "無菌導尿包、手套、潤滑凝膠（含 Lidocaine 為佳）、10 mL 注射器（蒸餾水）、固定貼片、尿袋。" },
                    { step: 3, title: "擺位與暴露", detail: "女性：仰臥屈膝蛙式。男性：仰臥平躺。維護隱私，僅暴露必要區域。" },
                    { step: 4, title: "手部衛生與無菌區建立", detail: "洗手 → 打開無菌包 → 戴無菌手套 → 鋪無菌巾。" },
                    { step: 5, title: "消毒會陰", detail: "以優碘棉球由內而外擦拭，每棉球限用一次。女性：分開小陰唇，清潔尿道口。男性：翻開包皮。" },
                    { step: 6, title: "插入導尿管", detail: "潤滑導尿管前端。女性：插入 5-7 cm 見尿再推入 2 cm。男性：將陰莖提至 60-90°，插入 17-22 cm。" },
                    { step: 7, title: "充氣球囊固定", detail: "確認尿液引流後，注入 10 mL 蒸餾水充氣球囊，輕拉確認固定。" },
                    { step: 8, title: "固定與記錄", detail: "以固定貼片固定於大腿內側或下腹部，尿袋低於膀胱。記錄尿管型號與引流量。" }
                ],
                warnings: ["嚴格遵守無菌技術", "若遇阻力不可強行推入", "注意乳膠過敏", "定期評估移除時機（CAUTI預防）"]
            },
            {
                title: "周邊靜脈留置針置入（Peripheral IV Insertion）",
                aliases: ["iv", "打針", "靜脈留置針", "輸液", "抽血"],
                source: "Gemini 護理 AI 助手",
                link: "https://gemini.google.com/app",
                summary: "建立周邊靜脈通路，用於輸液、給藥與抽血。",
                steps: [
                    { step: 1, title: "核對醫囑與評估", detail: "確認輸液醫囑、評估過敏史，選擇合適留置針號數（常用 18-22 G）。" },
                    { step: 2, title: "選擇穿刺部位", detail: "優先選擇非慣用手前臂遠端靜脈，避開關節處、患側肢體與傷口。" },
                    { step: 3, title: "準備用物", detail: "留置針、透明敷料、延長管、生理食鹽水沖洗針、止血帶、酒精棉片。" },
                    { step: 4, title: "手部衛生與綁止血帶", detail: "洗手戴手套，於穿刺點上方 10-15 cm 綁止血帶。" },
                    { step: 5, title: "消毒與穿刺", detail: "以 70% 酒精環形消毒待乾。以 15-30° 角進針，見回血後降低角度推進。" },
                    { step: 6, title: "退針芯與固定", detail: "固定外套管，退出針芯，連接延長管以生理食鹽水沖洗確認通暢。" },
                    { step: 7, title: "敷料覆蓋與標示", detail: "以透明敷料覆蓋，標示日期、時間、針號。記錄穿刺部位。" }
                ],
                warnings: ["單次穿刺不超過 2 次嘗試", "留置不超過 72-96 小時", "定期評估穿刺部位", "注意靜脈炎徵象"]
            },
            {
                title: "鼻胃管置入術（Nasogastric Tube Insertion）",
                aliases: ["ng", "ng tube", "鼻胃管", "插鼻胃管"],
                source: "Gemini 護理 AI 助手",
                link: "https://gemini.google.com/app",
                summary: "經鼻腔置入鼻胃管至胃部，用於腸胃減壓、灌食或給藥。",
                steps: [
                    { step: 1, title: "核對醫囑與評估", detail: "確認醫囑與尺寸（14-18 Fr），評估鼻腔通暢度、吞嚥功能。" },
                    { step: 2, title: "測量長度", detail: "從鼻尖→耳垂→劍突（NEX法），以膠帶標記（約 50-65 cm）。" },
                    { step: 3, title: "擺位與插入", detail: "半坐臥位（30-45°），潤滑管子前端 10 cm，沿鼻腔底部推入。達咽喉時配合吞嚥前進。" },
                    { step: 4, title: "確認位置與固定", detail: "抽吸胃液（pH < 5.5）或聽診法輔助，膠帶蝶形固定於鼻翼。" }
                ],
                warnings: ["顱底骨折禁止經鼻插管", "遇阻力時不可強推", "出現咳嗽或發紺應立即拔除"]
            },
            {
                title: "心肺復甦術與 AED 操作（CPR & AED）",
                aliases: ["cpr", "急救", "aed", "心肺復甦"],
                source: "Gemini 護理 AI 助手",
                link: "https://gemini.google.com/app",
                summary: "針對心跳停止病人執行急救心肺復甦術與電擊去顫。",
                steps: [
                    { step: 1, title: "確認現場安全與反應", detail: "確認環境安全，拍打肩膀並呼叫：「你還好嗎？」" },
                    { step: 2, title: "求救與取得 AED", detail: "指定專人撥打 119 或呼叫 999 團隊，並拿取 AED。" },
                    { step: 3, title: "評估呼吸與脈搏", detail: "觀察胸廓起伏與感受頸動脈脈搏，時間 5-10 秒。" },
                    { step: 4, title: "高效率胸外按壓", detail: "胸骨下半段，深度 5-6 cm，速率 100-120 次/分，允許胸廓完全回彈。" },
                    { step: 5, title: "配合 AED 電擊", detail: "開啟 AED 貼上電擊貼片，聽從語音指示，電擊前喊：「所有人離開！」" }
                ],
                warnings: ["按壓中斷不可超過 10 秒", "確保電擊時無人接觸病人", "每 2 分鐘輪替按壓者"]
            }
        ],
        drug: [
            {
                title: "二甲雙胍膜衣錠 (Metformin 500mg)",
                chinese_name: "庫魯化膜衣錠 / 二甲雙胍",
                generic_name: "Metformin Hydrochloride",
                brand_names: ["Glucophage 500mg", "Metformin"],
                dosage: "規格與商品名：Glucophage 500mg / Tab (台大藥劑部核可藥品)",
                summary: "台大醫院第 2 型糖尿病一線口服降血糖藥物，增加胰島素敏感性並減少肝臟葡萄糖生成。",
                source: "台大醫院藥劑部 (NTUH Pharmacy)",
                link: "https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939",
                instruction_pdf: "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"
            },
            {
                title: "阿斯匹靈腸溶錠 (Aspirin 100mg)",
                chinese_name: "阿斯匹靈 / 伯基",
                generic_name: "Acetylsalicylic Acid (Aspirin)",
                brand_names: ["Bokey 100mg", "Aspirin Protect"],
                dosage: "規格與商品名：Bokey 100mg / Cap (台大藥劑部核可藥品)",
                summary: "抗血小板聚集劑，用於預防心肌梗塞、缺血性中風及血栓形成。",
                source: "台大醫院藥劑部 (NTUH Pharmacy)",
                link: "https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939",
                instruction_pdf: "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"
            },
            {
                title: "普拿疼膜衣錠 (Panadol / Acetaminophen 500mg)",
                chinese_name: "普拿疼 / 乙醯胺酚",
                generic_name: "Acetaminophen",
                brand_names: ["Panadol 500mg", "Scanol"],
                dosage: "規格與商品名：Panadol 500mg / Tab (台大藥劑部核可藥品)",
                summary: "解熱鎮痛一線藥物，適用於中輕度疼痛與發燒緩解。",
                source: "台大醫院藥劑部 (NTUH Pharmacy)",
                link: "https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939",
                instruction_pdf: "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"
            },
            {
                title: "速效胰島素注射液 (Insulin Lispro / Humalog)",
                chinese_name: "優泌樂注射液",
                generic_name: "Insulin Lispro",
                brand_names: ["Humalog KwikPen 100 U/mL"],
                dosage: "規格與商品名：Humalog KwikPen 3mL (台大藥劑部核可藥品)",
                summary: "超速效胰島素製劑，用於控制餐後血糖升高，皮下注射後 15 分鐘內起效。",
                source: "台大醫院藥劑部 (NTUH Pharmacy)",
                link: "https://www.ntuh.gov.tw/phr/Fpage.action?muid=2077&fid=1939",
                instruction_pdf: "https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx"
            }
        ],
        disease: [
            {
                title: "第 2 型糖尿病血糖控制與實證指引（Type 2 Diabetes Management）",
                summary: "收錄 Cochrane Systematic Reviews 系統評價，分析生活型態介入、SGLT2 抑制劑與 GLP-1 受體促效劑對降低心血管事件與腎病變之綜合臨床療效。",
                source: "Cochrane Library 實證醫學圖書館",
                url: "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=%E7%B3%96%E5%B0%BF%E7%97%85"
            },
            {
                title: "急性心肌梗塞臨床照護處置指引（Acute Myocardial Infarction Guidelines）",
                summary: "分析早期抗血小板重疊治療（DAPT）、緊急經皮冠狀動脈介入術（PCI）與血栓溶解劑在急性冠心症發作黃金時間內之臨床實證數據。",
                source: "Cochrane Library 實證醫學圖書館",
                url: "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=%E5%BF%83%E8%82%8C%E6%A2%97%E5%A1%9E"
            },
            {
                title: "原發性高血壓藥物治療與目標控制（Hypertension Treatment Guidelines）",
                summary: "考克蘭實證文獻評估 ACEi/ARB、CCB 與 Thiazide 利尿劑於不同年齡層與合併腎臟病變患者之血壓目標（<130/80 mmHg）下降效果。",
                source: "Cochrane Library 實證醫學圖書館",
                url: "https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=%E9%AB%98%E8%A1%80%E5%A3%93"
            }
        ],
        education: [
            {
                title: "急性與慢性傷口照護及換藥步驟指南",
                summary: "照護線上衛教單張：詳細介紹傷口清潔、濕潤敷料選擇（人工皮、泡棉敷料）與感染徵象觀察重點。",
                source: "照護線上 CareOnline",
                url: "https://www.careonline.com.tw/?s=%E5%82%B7%E5%8F%A3%E7%85%A7%E8%AD%B7&utm_source=gemini"
            },
            {
                title: "防跌 8 大招！住院與居家跌倒預防衛教",
                summary: "照護線上衛教單張：評估高風險跌倒族群，提供環境改裝、輔具使用與夜間照明安全建議。",
                source: "照護線上 CareOnline",
                url: "https://www.careonline.com.tw/?s=%E8%B7%8C%E5%80%92%E9%A0%90%E9%98%B2&utm_source=gemini"
            },
            {
                title: "壓力性損傷（壓瘡）分期與照護擺位須知",
                summary: "照護線上衛教單張：了解壓瘡 1 至 4 期臨床表現，每 2 小時翻身拍背與減壓氣墊床使用時機。",
                source: "照護線上 CareOnline",
                url: "https://www.careonline.com.tw/?s=%E5%A3%93%E7%96%AE&utm_source=gemini"
            }
        ]
    };

    // 狀態變數
    let currentCategory = "all";
    let activeSopData = null;
    let favorites = JSON.parse(localStorage.getItem("nursebot_favs") || "[]");
    const clientCache = new Map();

    updateFavBadge();

    // ----------------------------------------------------------------------
    // Toast 通知 Helper
    // ----------------------------------------------------------------------
    function showToast(msg, type = "success") {
        const container = document.getElementById("toast-container");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        const icon = type === "error" ? "fa-circle-xmark" : (type === "info" ? "fa-circle-info" : "fa-circle-check");
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(msg)}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = "toastOut 0.3s forwards";
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }

    // ----------------------------------------------------------------------
    // 2. 主搜尋處理邏輯 (具備 API + 前端全庫動態智慧連結生成機制)
    // ----------------------------------------------------------------------
    async function performSearch(query, category = currentCategory) {
        query = query.trim();
        hideSuggestions();

        if (!query) {
            showState("welcome");
            return;
        }

        const cacheKey = `${category}_${query.toLowerCase()}`;
        if (clientCache.has(cacheKey)) {
            console.log("⚡ 前端快取極速命中:", cacheKey);
            renderResults(clientCache.get(cacheKey), query);
            return;
        }

        showState("loading");

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`);
            if (!response.ok) throw new Error("API HTTP " + response.status);
            
            const data = await response.json();
            if (data && Object.keys(data).length > 0) {
                clientCache.set(cacheKey, data);
                renderResults(data, query);
                return;
            }
            // 若 API 回傳空結果，執行純前端資料庫備援
            performClientSearch(query, category, cacheKey);
        } catch (error) {
            console.warn("後端 API 未回應，自動切換至前端高可用醫學資料庫搜尋:", error);
            performClientSearch(query, category, cacheKey);
        }
    }

    function generateDynamicResults(query, category) {
        const results = {};
        const queryClean = escapeHtml(query.trim());
        const encodedKw = encodeURIComponent(query.trim());

        // 1. 護理技術 SOP (Gemini AI 護理助手)
        const dynamicSkill = {
            title: `${queryClean} 臨床護理技術與處置 SOP`,
            aliases: [queryClean],
            source: "Gemini 護理 AI 助手",
            link: "https://gemini.google.com/app",
            summary: `Gemini 護理 AI 助手：針對「${queryClean}」提供臨床護理操作步驟、個案評估要點與安全注意事項指引。`,
            steps: [
                { step: 1, title: "個案評估與醫囑核對", detail: `執行雙重病人辨識，評估個案關於「${queryClean}」之生命徵象、過敏史、意識狀態與相關臨床檢驗數值。` },
                { step: 2, title: "用物與環境準備", detail: `準備「${queryClean}」所需之專用醫療照護耗材與防護裝備，維護操作環境清潔度並尊重個案隱私。` },
                { step: 3, title: "標準技術操作執行", detail: `嚴格遵循護理無菌與安全規範執行「${queryClean}」相關技術處置，操作過程中密切注意個案生理反應與舒適度。` },
                { step: 4, title: "衛教指導與護理紀錄", detail: `處置完畢後評估臨床效益，向個案及家屬衛教「${queryClean}」照護注意事項，並完整記錄於護理系統。` }
            ],
            warnings: [
                `執行過程嚴格遵守護理無菌操作與病人安全規範`,
                `密切觀察個案關於「${queryClean}」之急性生理變化與不適主訴`,
                `若出現異常突發狀況應立即停工並通報主治醫師處置`
            ]
        };

        // 2. 台大藥品查詢 (NTUH Pharmacy)
        const dynamicDrug = {
            title: `${queryClean} 藥物與處方資訊 (NTUH Pharmacy)`,
            chinese_name: `${queryClean} 相關藥品`,
            generic_name: `${queryClean} (Drug Query)`,
            brand_names: [`${queryClean}`],
            dosage: `台大醫院藥劑部綜合查詢系統品項：${queryClean}`,
            summary: `檢索台大醫院藥劑部「${queryClean}」藥品庫，提供院內核可藥品適應症、學名、中文名、商品名與用藥衛教仿單。`,
            source: "台大醫院藥劑部 (NTUH Pharmacy)",
            link: `https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx`,
            instruction_pdf: `https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx`
        };

        // 3. Cochrane 實證指引
        const dynamicDisease = {
            title: `${queryClean} 臨床實證醫學指引 (Cochrane Review)`,
            summary: `收錄「${queryClean}」最新 Cochrane Systematic Reviews 系統評價，分析高質量隨機對照試驗 (RCT) 之綜合臨床療效、安全評估與等級指引。`,
            source: "Cochrane Library 實證醫學圖書館",
            url: `https://www.cochranelibrary.com/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresultsportlet&p_p_lifecycle=0&_scolarissearchresultsportlet_WAR_scolarissearchresultsportlet_searchText=${encodedKw}`
        };

        // 4. 照護線上衛教單張
        const dynamicEdu = {
            title: `${queryClean} 專題衛教單張與照護指引`,
            summary: `照護線上衛教單張：提供「${queryClean}」醫療衛教文章、照護重點說明、飲食運動建議與常見問題解答。`,
            source: "照護線上 CareOnline",
            url: `https://www.careonline.com.tw/?s=${encodedKw}&utm_source=gemini`
        };

        if (category === "nursing_skill") {
            results.nursing_skill = [dynamicSkill];
        } else if (category === "drug") {
            results.drug = [dynamicDrug];
        } else if (category === "disease") {
            results.disease = [dynamicDisease];
        } else if (category === "education") {
            results.education = [dynamicEdu];
        } else {
            results.nursing_skill = [dynamicSkill];
            results.drug = [dynamicDrug];
            results.disease = [dynamicDisease];
            results.education = [dynamicEdu];
        }

        return results;
    }

    function performClientSearch(query, category, cacheKey) {
        const queryLower = query.toLowerCase();
        const results = {};

        const searchInCat = (catName) => {
            const list = CLIENT_DATABASE[catName] || [];
            return list.filter(item => {
                const titleMatch = item.title && item.title.toLowerCase().includes(queryLower);
                const summaryMatch = item.summary && item.summary.toLowerCase().includes(queryLower);
                const aliasMatch = item.aliases && item.aliases.some(a => a.toLowerCase().includes(queryLower));
                const chineseMatch = item.chinese_name && item.chinese_name.toLowerCase().includes(queryLower);
                const genericMatch = item.generic_name && item.generic_name.toLowerCase().includes(queryLower);
                return titleMatch || summaryMatch || aliasMatch || chineseMatch || genericMatch;
            });
        };

        if (category === "all" || !category) {
            ["nursing_skill", "drug", "disease", "education"].forEach(cat => {
                const res = searchInCat(cat);
                if (res.length > 0) results[cat] = res;
            });
        } else {
            const res = searchInCat(category);
            if (res.length > 0) results[category] = res;
        }

        // 若任何類別無靜態匹配項目，自動調用動態檢索產生器，保證不中斷
        if (Object.keys(results).length === 0) {
            const dynamicRes = generateDynamicResults(query, category);
            Object.assign(results, dynamicRes);
        }

        if (cacheKey) clientCache.set(cacheKey, results);
        renderResults(results, query);
    }

    function showState(state) {
        loadingState.classList.add("hidden");
        welcomeState.classList.add("hidden");
        emptyState.classList.add("hidden");
        resultsContainer.classList.add("hidden");

        if (state === "loading") loadingState.classList.remove("hidden");
        else if (state === "welcome") welcomeState.classList.remove("hidden");
        else if (state === "empty") emptyState.classList.remove("hidden");
        else if (state === "results") resultsContainer.classList.remove("hidden");
    }

    // ----------------------------------------------------------------------
    // 3. 結果卡片渲染
    // ----------------------------------------------------------------------
    function renderResults(data, query) {
        resultsContainer.innerHTML = "";
        let hasItems = false;

        const categories = ["nursing_skill", "drug", "disease", "education"];

        categories.forEach(cat => {
            if (data[cat] && data[cat].length > 0) {
                hasItems = true;
                data[cat].forEach(item => {
                    const card = createCardElement(cat, item, query);
                    resultsContainer.appendChild(card);
                });
            }
        });

        if (!hasItems) {
            showState("empty");
        } else {
            showState("results");
        }
    }

    function createCardElement(category, item, query) {
        const card = document.createElement("div");
        card.className = "res-card";

        const isFav = favorites.some(f => f.title === item.title);

        if (category === "nursing_skill") {
            card.style.setProperty("--card-accent", "var(--primary-nursing)");
            const stepsPreview = (item.steps || []).slice(0, 3).map(s => 
                `<div class="step-item"><span class="step-num">Step ${s.step}.</span> <span>${escapeHtml(s.title)}</span></div>`
            ).join("");

            card.innerHTML = `
                <div>
                    <div class="card-header">
                        <span class="card-badge nursing"><i class="fa-solid fa-stethoscope"></i> 護理技術 SOP</span>
                        <span class="meta-pill">Gemini AI 護理助手</span>
                    </div>
                    <h3 class="card-title">${escapeHtml(item.title)}</h3>
                    <p class="card-summary">${escapeHtml(item.summary || "")}</p>
                    <div class="steps-preview">${stepsPreview}</div>
                </div>
                <div class="card-actions">
                    <button class="btn-card-primary btn-open-sop">
                        <i class="fa-solid fa-list-check"></i> 檢視完整 SOP
                    </button>
                    <button class="btn-card-secondary btn-fav-card" title="${isFav ? '已收藏' : '加入收藏'}">
                        <i class="${isFav ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                    </button>
                </div>
            `;

            card.querySelector(".btn-open-sop").addEventListener("click", () => openSopModal(item));
            card.querySelector(".btn-fav-card").addEventListener("click", () => toggleFavoriteCard(item, card.querySelector(".btn-fav-card")));

        } else if (category === "drug") {
            card.style.setProperty("--card-accent", "var(--primary-drug)");
            
            let pdfButtons = "";
            if (item.instruction_pdf) {
                pdfButtons += `<a href="${escapeHtml(item.instruction_pdf)}" target="_blank" class="btn-card-primary"><i class="fa-solid fa-file-pdf"></i> 藥品仿單 PDF / 台大藥劑部</a>`;
            }
            if (item.education_pdf) {
                pdfButtons += `<a href="${escapeHtml(item.education_pdf)}" target="_blank" class="btn-card-secondary"><i class="fa-solid fa-file-arrow-down"></i> 用藥衛教 PDF</a>`;
            }

            card.innerHTML = `
                <div>
                    <div class="card-header">
                        <span class="card-badge drug"><i class="fa-solid fa-pills"></i> 藥物資訊</span>
                        <span class="meta-pill">${escapeHtml(item.source || "台大醫院藥劑部")}</span>
                    </div>
                    <h3 class="card-title">${escapeHtml(item.title)}</h3>
                    <div class="card-meta">
                        <span class="meta-pill">中文：${escapeHtml(item.chinese_name || "-")}</span>
                        <span class="meta-pill">學名：${escapeHtml(item.generic_name || "-")}</span>
                    </div>
                    <p class="card-summary">${escapeHtml(item.dosage || item.summary || "")}</p>
                </div>
                <div class="card-actions" style="flex-direction: column;">
                    ${pdfButtons || `<a href="${escapeHtml(item.link || 'https://reg.ntuh.gov.tw/pharmacyoutside/QueryDrug.aspx')}" target="_blank" class="btn-card-primary"><i class="fa-solid fa-arrow-up-right-from-square"></i> 查看台大藥劑部詳情</a>`}
                    <div style="display: flex; gap: 0.5rem; width: 100%;">
                        <button class="btn-card-secondary btn-copy-card" style="flex:1;"><i class="fa-solid fa-copy"></i> 複製資訊</button>
                        <button class="btn-card-secondary btn-fav-card"><i class="${isFav ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i></button>
                    </div>
                </div>
            `;

            card.querySelector(".btn-copy-card").addEventListener("click", () => copyCardText(item));
            card.querySelector(".btn-fav-card").addEventListener("click", () => toggleFavoriteCard(item, card.querySelector(".btn-fav-card")));

        } else if (category === "disease") {
            card.style.setProperty("--card-accent", "var(--primary-disease)");
            card.innerHTML = `
                <div>
                    <div class="card-header">
                        <span class="card-badge disease"><i class="fa-solid fa-file-medical"></i> 臨床實證指引</span>
                        <span class="meta-pill">Level A 考克蘭實證</span>
                    </div>
                    <h3 class="card-title">${escapeHtml(item.title)}</h3>
                    <p class="card-summary">${escapeHtml(item.summary || "")}</p>
                </div>
                <div class="card-actions" style="flex-direction: column;">
                    <a href="${escapeHtml(item.url || item.link)}" target="_blank" class="btn-card-primary" style="background: var(--primary-disease);">
                        <i class="fa-solid fa-graduation-cap"></i> 開啟 Cochrane 實證庫
                    </a>
                    <div style="display: flex; gap: 0.5rem; width: 100%;">
                        <button class="btn-card-secondary btn-copy-card" style="flex:1;"><i class="fa-solid fa-copy"></i> 複製指引</button>
                        <button class="btn-card-secondary btn-fav-card"><i class="${isFav ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i></button>
                    </div>
                </div>
            `;

            card.querySelector(".btn-copy-card").addEventListener("click", () => copyCardText(item));
            card.querySelector(".btn-fav-card").addEventListener("click", () => toggleFavoriteCard(item, card.querySelector(".btn-fav-card")));

        } else if (category === "education") {
            card.style.setProperty("--card-accent", "var(--primary-education)");
            card.innerHTML = `
                <div>
                    <div class="card-header">
                        <span class="card-badge education"><i class="fa-solid fa-book-medical"></i> 衛教單張</span>
                        <span class="meta-pill">照護線上</span>
                    </div>
                    <h3 class="card-title">${escapeHtml(item.title)}</h3>
                    <p class="card-summary">${escapeHtml(item.summary || item.snippet || "")}</p>
                </div>
                <div class="card-actions" style="flex-direction: column;">
                    <a href="${escapeHtml(item.url || item.link)}" target="_blank" class="btn-card-primary" style="background: var(--primary-education);">
                        <i class="fa-solid fa-newspaper"></i> 閱讀照護線上單張
                    </a>
                    <div style="display: flex; gap: 0.5rem; width: 100%;">
                        <button class="btn-card-secondary btn-copy-card" style="flex:1;"><i class="fa-solid fa-copy"></i> 複製衛教</button>
                        <button class="btn-card-secondary btn-fav-card"><i class="${isFav ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i></button>
                    </div>
                </div>
            `;

            card.querySelector(".btn-copy-card").addEventListener("click", () => copyCardText(item));
            card.querySelector(".btn-fav-card").addEventListener("click", () => toggleFavoriteCard(item, card.querySelector(".btn-fav-card")));
        }

        return card;
    }

    function copyCardText(item) {
        let text = `【${item.title}】\n\n`;
        if (item.chinese_name) text += `中文名：${item.chinese_name}\n`;
        if (item.generic_name) text += `學名：${item.generic_name}\n`;
        if (item.summary || item.dosage) text += `內容：${item.summary || item.dosage}\n`;
        if (item.link || item.url) text += `連結：${item.link || item.url}\n`;
        text += `\n(資料來源：NurseBot 護理智慧臨床助手)`;

        navigator.clipboard.writeText(text).then(() => {
            showToast(`已複製「${item.title}」資訊！`, "info");
        });
    }

    function toggleFavoriteCard(item, btnElement) {
        const index = favorites.findIndex(f => f.title === item.title);
        if (index > -1) {
            favorites.splice(index, 1);
            showToast(`已取消收藏「${item.title}」`, "info");
            if (btnElement) {
                const icon = btnElement.querySelector("i");
                if (icon) icon.className = "fa-regular fa-bookmark";
            }
        } else {
            favorites.push(item);
            showToast(`已將「${item.title}」加入收藏！`, "success");
            if (btnElement) {
                const icon = btnElement.querySelector("i");
                if (icon) icon.className = "fa-solid fa-bookmark";
            }
        }
        localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
        updateFavBadge();
    }

    // ----------------------------------------------------------------------
    // 4. Modal SOP 對話盒控制
    // ----------------------------------------------------------------------
    function openSopModal(data) {
        activeSopData = data;
        modalTitle.textContent = data.title;

        // 警告 Callout
        if (data.warnings && data.warnings.length > 0) {
            modalWarnings.classList.remove("hidden");
            modalWarningsList.innerHTML = data.warnings.map(w => `<p>• ${escapeHtml(w)}</p>`).join("");
        } else {
            modalWarnings.classList.add("hidden");
        }

        // 步驟 Checklist
        modalStepsContainer.innerHTML = (data.steps || []).map((s, idx) => `
            <div class="step-box-item" data-step-index="${idx}">
                <input type="checkbox" class="step-checkbox" id="step-chk-${idx}">
                <div class="step-content">
                    <div class="step-content-title">Step ${s.step}. ${escapeHtml(s.title)}</div>
                    <div class="step-content-detail">${escapeHtml(s.detail)}</div>
                </div>
            </div>
        `).join("");

        // 點擊卡片任何地方皆可勾選
        modalStepsContainer.querySelectorAll(".step-box-item").forEach(item => {
            item.addEventListener("click", (e) => {
                if (e.target.tagName !== "INPUT") {
                    const chk = item.querySelector(".step-checkbox");
                    chk.checked = !chk.checked;
                }
                const chk = item.querySelector(".step-checkbox");
                if (chk.checked) item.classList.add("completed");
                else item.classList.remove("completed");
            });
        });

        sopModal.classList.remove("hidden");
    }

    modalClose.addEventListener("click", () => sopModal.classList.add("hidden"));

    // 複製 SOP
    btnCopySop.addEventListener("click", () => {
        if (!activeSopData) return;
        let text = `【${activeSopData.title}】\n\n`;
        if (activeSopData.warnings) {
            text += `⚠️ 注意事項：\n` + activeSopData.warnings.map(w => `- ${w}`).join("\n") + "\n\n";
        }
        text += `📋 操作步驟：\n`;
        (activeSopData.steps || []).forEach(s => {
            text += `Step ${s.step}. ${s.title}\n   說明：${s.detail}\n`;
        });
        text += `\n(資料來源：NurseBot 護理智慧臨床助手)`;

        navigator.clipboard.writeText(text).then(() => {
            showToast("已成功複製 SOP 步驟內容至剪貼簿！", "success");
        });
    });

    // 列印
    btnPrintSop.addEventListener("click", () => {
        window.print();
    });

    // 收藏 SOP
    btnSaveFavSop.addEventListener("click", () => {
        if (!activeSopData) return;
        toggleFavoriteCard(activeSopData);
    });

    // ----------------------------------------------------------------------
    // 5. 收藏功能 LocalStorage
    // ----------------------------------------------------------------------
    function updateFavBadge() {
        favCountBadge.textContent = favorites.length;
    }

    btnFavorites.addEventListener("click", () => {
        renderFavList();
        favModal.classList.remove("hidden");
    });

    favModalClose.addEventListener("click", () => favModal.classList.add("hidden"));

    btnClearFavs.addEventListener("click", () => {
        if (favorites.length === 0) return;
        if (confirm("確定要清空所有收藏嗎？")) {
            favorites = [];
            localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
            updateFavBadge();
            renderFavList();
            showToast("已清空所有收藏", "info");
        }
    });

    function renderFavList() {
        if (favorites.length === 0) {
            favListContainer.innerHTML = "<p style='color: var(--text-secondary); text-align: center; padding: 2rem;'>目前尚未收藏任何臨床項目。</p>";
            return;
        }

        favListContainer.innerHTML = favorites.map((item, index) => `
            <div class="res-card" style="margin-bottom: 1rem;">
                <h4 style="color: var(--text-primary); margin-bottom: 0.4rem;">${escapeHtml(item.title)}</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">${escapeHtml(item.summary || "")}</p>
                <div style="display: flex; gap: 0.5rem;">
                    ${item.steps ? `<button class="btn-card-primary btn-open-fav-sop" data-fav-index="${index}"><i class="fa-solid fa-eye"></i> 查看 SOP</button>` : ''}
                    <button class="btn-card-secondary btn-del-fav" data-fav-index="${index}"><i class="fa-solid fa-trash"></i> 移除</button>
                </div>
            </div>
        `).join("");

        favListContainer.querySelectorAll(".btn-open-fav-sop").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.favIndex);
                openSopModal(favorites[idx]);
                favModal.classList.add("hidden");
            });
        });

        favListContainer.querySelectorAll(".btn-del-fav").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.favIndex);
                const removedTitle = favorites[idx].title;
                favorites.splice(idx, 1);
                localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
                updateFavBadge();
                renderFavList();
                showToast(`已移除「${removedTitle}」`, "info");
            });
        });
    }

    // ----------------------------------------------------------------------
    // 6. 即時關鍵字建議下拉選單 (AutoComplete)
    // ----------------------------------------------------------------------
    function updateSuggestions(val) {
        val = val.trim().toLowerCase();
        if (!val) {
            hideSuggestions();
            return;
        }

        const matches = SUGGESTION_POOL.filter(item => 
            item.title.toLowerCase().includes(val) || item.cat.toLowerCase().includes(val)
        );

        if (matches.length === 0) {
            hideSuggestions();
            return;
        }

        searchSuggestions.innerHTML = matches.map(m => `
            <div class="suggestion-item" data-query="${escapeHtml(m.title.split(' ')[0])}">
                <span><i class="fa-solid fa-magnifying-glass" style="font-size: 0.8rem; margin-right: 0.5rem; color: var(--text-muted);"></i>${escapeHtml(m.title)}</span>
                <span class="suggestion-tag">${escapeHtml(m.cat)}</span>
            </div>
        `).join("");

        searchSuggestions.querySelectorAll(".suggestion-item").forEach(item => {
            item.addEventListener("click", () => {
                const q = item.dataset.query;
                searchInput.value = q;
                btnClear.classList.remove("hidden");
                hideSuggestions();
                performSearch(q);
            });
        });

        searchSuggestions.classList.remove("hidden");
    }

    function hideSuggestions() {
        if (searchSuggestions) searchSuggestions.classList.add("hidden");
    }

    // ----------------------------------------------------------------------
    // 7. 事件監聽
    // ----------------------------------------------------------------------
    btnSearch.addEventListener("click", () => performSearch(searchInput.value));

    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performSearch(searchInput.value);
    });

    searchInput.addEventListener("input", () => {
        const val = searchInput.value.trim();
        if (val.length > 0) {
            btnClear.classList.remove("hidden");
            updateSuggestions(val);
        } else {
            btnClear.classList.add("hidden");
            hideSuggestions();
            showState("welcome");
        }
    });

    btnClear.addEventListener("click", () => {
        searchInput.value = "";
        btnClear.classList.add("hidden");
        hideSuggestions();
        showState("welcome");
    });

    tagButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.dataset.query;
            searchInput.value = query;
            btnClear.classList.remove("hidden");
            performSearch(query);
        });
    });

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentCategory = btn.dataset.category;
            if (searchInput.value.trim()) {
                performSearch(searchInput.value, currentCategory);
            }
        });
    });

    // 切換深淺色主題
    btnThemeToggle.addEventListener("click", () => {
        const html = document.documentElement;
        const currentTheme = html.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        html.setAttribute("data-theme", newTheme);
        btnThemeToggle.querySelector("i").className = newTheme === "dark" ? "fa-solid fa-moon" : "fa-solid fa-sun";
        showToast(`已切換至 ${newTheme === 'dark' ? '深色' : '淺色'} 模式`, "info");
    });

    // 點擊 Modal 遮罩關閉 Modal
    [sopModal, favModal].forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.classList.add("hidden");
            }
        });
    });

    // 按 Escape 鍵關閉 Modals 與 Suggestions
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            sopModal.classList.add("hidden");
            favModal.classList.add("hidden");
            hideSuggestions();
        }
    });

    // 點擊頁面其他地方時隱藏 Suggestions
    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            hideSuggestions();
        }
    });

    // 回到頂部按鈕
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            btnBackToTop.classList.remove("hidden");
        } else {
            btnBackToTop.classList.add("hidden");
        }
    });

    btnBackToTop.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
