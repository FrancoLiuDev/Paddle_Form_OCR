# 11_PDF_Pipeline 專案結構

## 📁 完整目錄結構

```
11_PDF_Pipeline/                    # 主專案目錄
│
├── 📄 核心檔案
│   ├── pipeline.py                 # Pipeline 主程式
│   ├── pipeline_config.json        # Pipeline 配置
│   ├── run.sh                      # 執行腳本（一鍵運行）
│   └── requirements.txt            # Python 依賴套件
│
├── 📚 文檔
│   ├── README.md                   # 使用說明（主要文檔）
│   ├── ARCHITECTURE.md             # 架構設計文檔
│   ├── STEPS_CONFIG.md             # 步驟配置模板
│   ├── PACKAGING.md                # 打包指南
│   └── PROJECT_STRUCTURE.md        # 本檔案
│
├── 🔧 工具模組
│   └── tools/                      # 所有處理工具
│       ├── __init__.py             # 模組初始化
│       └── pdf_converter/          # PDF 轉圖片工具
│           ├── __init__.py         # 轉換器類別
│           └── pdf_to_images.py    # 轉換腳本
│
├── 📂 執行目錄
│   ├── input/                      # 輸入目錄（放置 PDF）
│   ├── meta/                       # 中間處理結果
│   │   └── step1_pdf_to_images/    # Step 1 的輸出
│   ├── output/                     # 最終結果
│   │   └── pipeline_result_*.json  # 執行報告
│   └── logs/                       # 執行日誌
│       └── step1.log               # Step 1 的日誌
│
└── 🛠️ 打包工具
    └── build_executable.sh         # PyInstaller 打包腳本
```

## 📝 檔案說明

### 核心檔案

#### pipeline.py
- **功能**：Pipeline 主程式
- **類別**：
  - `PipelineLogger`: 日誌管理
  - `Step1_PDFToImages`: PDF 轉圖片步驟
  - `Pipeline`: 主控制類別
- **依賴**：tools 模組
- **執行**：`python3 pipeline.py`

#### pipeline_config.json
- **功能**：Pipeline 配置檔
- **內容**：
  - 步驟定義
  - 參數設定
  - 輸入輸出路徑
- **格式**：JSON

#### run.sh
- **功能**：一鍵執行腳本
- **檢查**：
  - input 目錄存在
  - PDF 檔案數量
- **執行**：`./run.sh`

#### requirements.txt
- **功能**：Python 依賴清單
- **套件**：
  - PyMuPDF (PDF 處理)
  - Pillow (圖片處理)

### 文檔檔案

#### README.md
- **主要使用說明**
- 內容：
  - 快速開始
  - 使用方式
  - 故障排除
  - 執行範例

#### ARCHITECTURE.md
- **架構設計文檔**
- 內容：
  - 設計理念
  - 步驟定義格式
  - 日誌格式
  - 目錄結構

#### STEPS_CONFIG.md
- **步驟配置模板**
- 內容：
  - 填寫指南
  - 步驟模板
  - 範例說明

#### PACKAGING.md
- **打包指南**
- 內容：
  - 打包方案比較
  - PyInstaller 使用
  - Docker 打包
  - 最佳實踐

### 工具模組

#### tools/
獨立的工具模組，不依賴外部專案

**設計原則**：
- ✅ 封裝完整
- ✅ 可獨立使用
- ✅ 介面清晰
- ✅ 易於測試

**目前工具**：
- `pdf_converter`: PDF 轉圖片

**未來擴展**：
- `ocr_processor`: OCR 文字識別
- `image_processor`: 圖片預處理
- `data_formatter`: 資料格式化

### 執行目錄

#### input/
- **用途**：放置輸入 PDF 檔案
- **限制**：只能有一個 PDF
- **驗證**：Pipeline 啟動時檢查

#### meta/
- **用途**：存放中間處理結果
- **結構**：每個步驟一個子目錄
  - `step1_pdf_to_images/`: PDF 轉圖片輸出
  - `step2_*/`: 未來步驟的輸出
- **特性**：可追蹤每個步驟的輸出

#### output/
- **用途**：最終結果和報告
- **檔案**：
  - `pipeline_result_YYYYMMDD_HHMMSS.json`: 執行報告
  - 每次執行產生一個新報告
- **格式**：JSON，包含所有步驟的詳細資訊

#### logs/
- **用途**：詳細執行日誌
- **檔案**：每個步驟一個日誌
  - `step1.log`: Step 1 的日誌
  - `step2.log`: Step 2 的日誌（未來）
- **內容**：
  - 時間戳記
  - 輸入輸出資訊
  - 錯誤訊息
  - 執行狀態

## 🔄 資料流向

```
1. 用戶放入 PDF
   └─→ input/document.pdf

2. Pipeline 讀取配置
   └─→ pipeline_config.json

3. Step 1: PDF 轉圖片
   ├─→ 讀取: input/document.pdf
   ├─→ 使用: tools/pdf_converter
   ├─→ 輸出: meta/step1_pdf_to_images/*.png
   └─→ 紀錄: logs/step1.log

4. Step 2: (未來步驟)
   ├─→ 讀取: meta/step1_pdf_to_images/*.png
   ├─→ 使用: tools/??? 
   ├─→ 輸出: meta/step2_???/
   └─→ 紀錄: logs/step2.log

5. 產生最終報告
   └─→ output/pipeline_result_*.json
```

## 🎯 獨立性設計

### ✅ 已完成
- [x] 工具模組化（tools/）
- [x] 不依賴外部專案
- [x] 可獨立運行
- [x] 完整的錯誤處理
- [x] 詳細的日誌記錄

### 🔄 可打包方式
1. **PyInstaller**: 單一執行檔
2. **Docker**: 容器化部署
3. **Pip Package**: Python 套件
4. **Zip Archive**: 壓縮包分發

### 📦 打包後結構
```
pdf_pipeline                        # 執行檔
├── input/                          # 需手動建立
├── output/                         # 自動建立
├── logs/                           # 自動建立
└── meta/                           # 自動建立
```

## 🚀 快速開始

### 開發模式
```bash
# 1. 進入目錄
cd 11_PDF_Pipeline

# 2. 安裝依賴
pip3 install -r requirements.txt

# 3. 放入 PDF
cp your.pdf input/

# 4. 執行
./run.sh
```

### 打包模式
```bash
# 1. 打包
./build_executable.sh

# 2. 部署
cp dist/pdf_pipeline /target/location/

# 3. 使用
cd /target/location/
mkdir input
cp your.pdf input/
./pdf_pipeline
```

## 📊 檔案大小參考

- pipeline.py: ~10 KB
- tools/: ~8 KB
- 文檔: ~20 KB
- **總計**: ~40 KB（不含依賴）
- **打包後**: ~50-100 MB（含 Python 和依賴）

## 🔧 維護指南

### 添加新步驟
1. 在 `tools/` 創建新工具模組
2. 在 `pipeline.py` 添加步驟類別
3. 更新 `pipeline_config.json`
4. 更新 `STEPS_CONFIG.md`

### 更新工具
1. 修改 `tools/xxx/` 模組
2. 保持介面一致性
3. 更新對應文檔
4. 測試完整流程

### 版本管理
- 版本號在 `pipeline_config.json`
- 遵循語義化版本（Semantic Versioning）
- 重大更新更新主版本號

## ✅ 檢查清單

部署前確認：
- [ ] 所有 Python 檔案無語法錯誤
- [ ] requirements.txt 完整
- [ ] 文檔齊全且更新
- [ ] 測試通過（至少一個完整流程）
- [ ] 日誌功能正常
- [ ] 錯誤處理完善
- [ ] 配置檔案格式正確
