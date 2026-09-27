# 🏥 NurseBot 護理智慧助手

護理人員專用的 LINE 聊天機器人，只需輸入簡單指令，即可即時查詢護理技術操作、藥物資訊、臨床照護指引與衛教單張。

## ✨ 功能特色

| 指令 | 功能 | 資料來源 | 範例 |
|------|------|----------|------|
| `護+主題` | 🩺 護理技術操作步驟 | Gemini 護理 AI 助手 | `護+導尿管置入` |
| `藥+學名` | 💊 藥物資訊查詢 | 台大醫院藥劑部 NTUH | `藥+Metformin` |
| `病+疾病` | 📋 臨床照護指引 | Cochrane Library | `病+糖尿病` |
| `衛+主題` | 📄 衛教單張查詢 | 照護線上 CareOnline | `衛+傷口照護` |

### 支援的分隔符號
`+`、`＋`、`:`、`：`、`空格` 皆可使用，例如 `藥+Insulin`、`藥：Insulin`、`藥 Insulin`

### 回覆格式
- **Flex Message 卡片**：美觀的結構化卡片，含步驟編號、警語、護理重點
- **底部連結按鈕**：可直接前往資料庫查看完整內容

---

## 📁 專案結構

```
LINE機器人/
├── app.py              # Flask 主程式 + LINE Webhook
├── command_parser.py   # 指令解析器
├── ebsco_client.py     # EBSCO EDS API 客戶端
├── mock_data.py        # 模擬資料（開發測試用）
├── flex_builder.py     # Flex Message 卡片建構器
├── tests.py            # 單元測試（27 項）
├── requirements.txt    # Python 依賴套件
├── Procfile            # Render.com 部署設定
├── render.yaml         # Render.com IaC 設定
├── .env.example        # 環境變數範本
├── .env                # 環境變數（勿上傳）
└── .gitignore          # Git 排除規則
```

---

## 🚀 快速開始

### 1. 建立 LINE Messaging API Channel

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 以 LINE 帳號登入
3. 點選 **Create a new provider**（或選擇已有的 Provider）
4. 點選 **Create a Messaging API channel**
5. 填入：
   - Channel name: `護理智慧助手`（或自訂名稱）
   - Channel description: `護理技術操作與藥物查詢`
   - Category / Subcategory: `Health` → `Healthcare`
6. 建立後取得金鑰：
   - **Channel Secret**：`Basic settings` → Channel secret
   - **Channel Access Token**：`Messaging API` → 點擊 `Issue` 產生

> ⚠️ 在 `Messaging API` 頁面中，將 **Auto-reply messages** 設為 `Disabled`

### 2. 安裝與設定

```bash
# 複製專案
cd H:\LINE機器人

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
copy .env.example .env
# 編輯 .env，填入你的 LINE Channel Secret 和 Access Token
```

### 3. 本機測試（使用 ngrok）

```bash
# 啟動伺服器
python app.py

# 另開終端，使用 ngrok 建立公開網址
ngrok http 5000

# 複製 ngrok 產生的 https 網址，例如：
# https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

將 `https://xxxx.ngrok-free.app/callback` 填入 LINE Developers Console 的 **Webhook URL**，點擊 **Verify** 確認成功。

### 4. 部署到 Render.com

1. 將專案推上 GitHub
2. 前往 [Render.com](https://render.com)，點選 **New** → **Web Service**
3. 連接你的 GitHub repo
4. 設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. 在 **Environment** 加入環境變數：
   - `LINE_CHANNEL_SECRET` = 你的 Channel Secret
   - `LINE_CHANNEL_ACCESS_TOKEN` = 你的 Access Token
   - `USE_MOCK_DATA` = `true`
6. 部署完成後，將 Render 提供的網址 + `/callback` 填入 LINE Webhook URL

---

## 🔧 切換資料來源

### 模擬資料模式（預設）
```env
USE_MOCK_DATA=true
```
內建豐富的護理資料，包含 10 項護理技術、7 種藥物、5 種疾病指引、5 份衛教單張。適合開發測試。

### EBSCO EDS API 模式
```env
USE_MOCK_DATA=false
EBSCO_PROFILE_ID=your_profile_id
EBSCO_USER_ID=your_api_user
EBSCO_PASSWORD=your_password
```
需要有效的 EBSCO 機構訂閱。請聯繫貴機構圖書館或 EBSCO 業務代表取得 API 帳號。

---

## 🧪 執行測試

```bash
python -m pytest tests.py -v
```

---

## 📱 內建模擬資料涵蓋範圍

### 護理技術（護+）
導尿管置入、靜脈注射、鼻胃管置入、傷口換藥、抽血、氧氣治療、生命徵象測量、給藥技術、CPR、血糖監測

### 藥物資訊（藥+）
Metformin、Insulin、Warfarin、Heparin、Digoxin、Amlodipine、Enoxaparin

### 疾病指引（病+）
糖尿病、高血壓、肺炎、心衰竭、中風

### 衛教單張（衛+）
傷口照護、糖尿病飲食、跌倒預防、壓瘡預防、手術前準備

---

## 📄 授權
本專案僅供教育與開發測試用途。模擬資料參考公開護理教科書與藥典，不構成醫療建議。
連接 EBSCO 資料庫時，請遵守貴機構的授權協議。
