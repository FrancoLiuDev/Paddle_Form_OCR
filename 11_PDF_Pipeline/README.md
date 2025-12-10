# 11_PDF_Pipeline

## �� 專案說明

這是一個**步驟化的 PDF 處理 Pipeline**，讓您能清楚追蹤每個步驟的輸入、處理、輸出。

### ✨ 特色

- ✅ **步驟化處理**：每個步驟獨立執行，清楚記錄
- ✅ **完整追蹤**：詳細的日誌記錄每個步驟的 I/O
- ✅ **易於擴展**：可隨時添加新步驟
- ✅ **失敗保護**：某步驟失敗自動中止後續步驟

## 📁 目錄結構

\`\`\`
11_PDF_Pipeline/
├── input/              # 輸入 PDF 檔案（只能有一個）
├── meta/               # 中間處理結果
│   ├── step1_pdf_to_images/   # Step 1 的輸出
│   ├── step2_???/             # Step 2 的輸出
│   └── ...
├── output/             # 最終結果和執行報告
├── logs/               # 每個步驟的詳細日誌
├── pipeline_config.json    # Pipeline 配置
├── pipeline.py             # Pipeline 主程式
└── run.sh                  # 執行腳本
\`\`\`

## 🚀 使用說明

### 1. 準備輸入檔案

將**一個** PDF 檔案放入 \`input/\` 目錄：

\`\`\`bash
cp your_document.pdf input/
\`\`\`

⚠️ **注意**：\`input/\` 目錄只能有一個 PDF 檔案！

### 2. 執行 Pipeline

\`\`\`bash
./run.sh
\`\`\`

或直接執行 Python 腳本：

\`\`\`bash
python3 pipeline.py
\`\`\`

### 3. 查看結果

- **最終結果**：\`output/pipeline_result_YYYYMMDD_HHMMSS.json\`
- **詳細日誌**：\`logs/step1.log\`, \`logs/step2.log\`, ...
- **中間檔案**：\`meta/step1_???/\`, \`meta/step2_???/\`, ...

## 🔧 目前的步驟

### Step 1: PDF 轉圖片 ✅

- **輸入**：\`input/*.pdf\`
- **處理**：使用 \`8_PDF_To_Images\` 工具
- **輸出**：\`meta/step1_pdf_to_images/*.png\`
- **參數**：DPI 300, PNG 格式, RGB 色彩

### Step 2: （待定義）

請編輯 \`STEPS_CONFIG.md\` 來定義後續步驟。

## 📝 添加新步驟

1. 編輯 \`STEPS_CONFIG.md\`，填寫新步驟的資訊
2. 更新 \`pipeline_config.json\`，添加步驟配置
3. 在 \`pipeline.py\` 中實作對應的步驟類別
4. 測試執行

## 🐛 故障排除

### 錯誤：input/ 目錄中沒有 PDF 檔案

**解決**：將 PDF 檔案複製到 \`input/\` 目錄

### 錯誤：input/ 目錄中有多個 PDF 檔案

**解決**：確保 \`input/\` 只有一個 PDF 檔案

### 某個步驟執行失敗

查看對應的日誌檔案：

\`\`\`bash
cat logs/step1.log
\`\`\`

## 📖 相關文件

- [ARCHITECTURE.md](ARCHITECTURE.md) - Pipeline 架構設計
- [STEPS_CONFIG.md](STEPS_CONFIG.md) - 步驟配置模板
