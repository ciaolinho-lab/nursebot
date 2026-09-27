/**
 * NurseBot 護理智慧查詢網 - JavaScript Web Client
 */

document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------------------------
    // 1. DOM 元素選取
    // ----------------------------------------------------------------------
    const searchInput = document.getElementById("search-input");
    const btnSearch = document.getElementById("btn-search");
    const btnClear = document.getElementById("btn-clear");
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

    // 狀態變數
    let currentCategory = "all";
    let activeSopData = null;
    let favorites = JSON.parse(localStorage.getItem("nursebot_favs") || "[]");

    updateFavBadge();

    // ----------------------------------------------------------------------
    // 2. 主搜尋處理邏輯
    // ----------------------------------------------------------------------
    async function performSearch(query, category = currentCategory) {
        query = query.trim();
        if (!query) {
            showState("welcome");
            return;
        }

        showState("loading");

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`);
            if (!response.ok) throw new Error("HTTP error " + response.status);
            
            const data = await response.json();
            renderResults(data, query);
        } catch (error) {
            console.error("Search error:", error);
            showState("empty");
        }
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
                </div>
            `;

            card.querySelector(".btn-open-sop").addEventListener("click", () => openSopModal(item));

        } else if (category === "drug") {
            card.style.setProperty("--card-accent", "var(--primary-drug)");
            
            let pdfButtons = "";
            if (item.instruction_pdf) {
                pdfButtons += `<a href="${escapeHtml(item.instruction_pdf)}" target="_blank" class="btn-card-primary"><i class="fa-solid fa-file-pdf"></i> 下載藥品仿單 PDF</a>`;
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
                    ${pdfButtons || `<a href="${escapeHtml(item.link || '#')}" target="_blank" class="btn-card-primary"><i class="fa-solid fa-arrow-up-right-from-square"></i> 查看台大藥劑部詳情</a>`}
                </div>
            `;

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
                <div class="card-actions">
                    <a href="${escapeHtml(item.url || item.link)}" target="_blank" class="btn-card-primary" style="background: var(--primary-disease);">
                        <i class="fa-solid fa-graduation-cap"></i> 開啟 Cochrane 實證庫
                    </a>
                </div>
            `;

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
                <div class="card-actions">
                    <a href="${escapeHtml(item.url || item.link)}" target="_blank" class="btn-card-primary" style="background: var(--primary-education);">
                        <i class="fa-solid fa-newspaper"></i> 閱讀照護線上完整單張
                    </a>
                </div>
            `;
        }

        return card;
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
            alert("已成功複製 SOP 步驟內容至剪貼簿！");
        });
    });

    // 列印
    btnPrintSop.addEventListener("click", () => {
        window.print();
    });

    // 收藏 SOP
    btnSaveFavSop.addEventListener("click", () => {
        if (!activeSopData) return;
        saveFavorite(activeSopData);
        alert(`已將「${activeSopData.title}」加入我的收藏！`);
    });

    // ----------------------------------------------------------------------
    // 5. 收藏功能 LocalStorage
    // ----------------------------------------------------------------------
    function saveFavorite(item) {
        if (!favorites.some(f => f.title === item.title)) {
            favorites.push(item);
            localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
            updateFavBadge();
        }
    }

    function updateFavBadge() {
        favCountBadge.textContent = favorites.length;
    }

    btnFavorites.addEventListener("click", () => {
        renderFavList();
        favModal.classList.remove("hidden");
    });

    favModalClose.addEventListener("click", () => favModal.classList.add("hidden"));

    btnClearFavs.addEventListener("click", () => {
        if (confirm("確定要清空所有收藏嗎？")) {
            favorites = [];
            localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
            updateFavBadge();
            renderFavList();
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
                favorites.splice(idx, 1);
                localStorage.setItem("nursebot_favs", JSON.stringify(favorites));
                updateFavBadge();
                renderFavList();
            });
        });
    }

    // ----------------------------------------------------------------------
    // 6. 事件監聽 (搜尋框、熱門標籤、頁籤、主題切換)
    // ----------------------------------------------------------------------
    btnSearch.addEventListener("click", () => performSearch(searchInput.value));

    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performSearch(searchInput.value);
    });

    searchInput.addEventListener("input", () => {
        if (searchInput.value.trim().length > 0) {
            btnClear.classList.remove("hidden");
        } else {
            btnClear.classList.add("hidden");
        }
    });

    btnClear.addEventListener("click", () => {
        searchInput.value = "";
        btnClear.classList.add("hidden");
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
