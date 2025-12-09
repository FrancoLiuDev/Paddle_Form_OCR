# 8_PDF_IMAGES - PDF 轉圖片工具

高品質 PDF 轉圖片工具，專為文件掃描和 OCR 預處理設計。

## 功能特色

✅ **最高品質輸出**
- 支援自訂 DPI (預設 300，可達 600+)
- PNG 無損格式或 JPEG 高品質壓縮
- 自動最佳化壓縮，平衡品質與檔案大小

✅ **批次處理**
- 自動處理 PDF 所有頁面
- 自動建立輸出目錄結構
- 顯示處理進度和統計資訊

✅ **彈性設定**
- 可調整解析度 (150/300/600 DPI)
- 可選擇圖片格式 (PNG/JPEG)
- 可自訂輸出目錄

## 安裝依賴

```bash
pip install -r requirements.txt
```

或手動安裝：
```bash
pip install PyMuPDF Pillow
```

## 使用方式

### 基本使用 (預設 300 DPI, PNG 格式)

```bash
python pdf_to_images.py input/013大安.pdf
```

### 高品質模式 (600 DPI)

```bash
python pdf_to_images.py input/013大安.pdf --dpi 600
```

### 使用 JPEG 格式 (檔案較小)

```bash
python pdf_to_images.py input/013大安.pdf --format JPG
```

### 自訂輸出目錄

```bash
python pdf_to_images.py input/013大安.pdf --output my_images
```

### 完整參數範例

```bash
python pdf_to_images.py input/013大安.pdf --dpi 600 --format PNG --output high_quality
```

## 參數說明

| 參數 | 說明 | 預設值 | 建議值 |
|------|------|--------|--------|
| `pdf_file` | PDF 檔案路徑 | (必填) | - |
| `--dpi` | 解析度 (DPI) | 300 | 150(快速), 300(標準), 600(高品質) |
| `--format` | 圖片格式 | PNG | PNG(無損), JPG(壓縮) |
| `--output` | 輸出目錄 | output | 任意目錄名稱 |

## DPI 選擇建議

- **150 DPI**: 快速預覽，檔案小 (~200KB/頁)
- **300 DPI**: 標準品質，適合一般 OCR (~500KB/頁)
- **600 DPI**: 高品質，適合精細文件 (~2MB/頁)

## 格式選擇建議

- **PNG**: 無損壓縮，最高品質，檔案較大，適合需要後續處理
- **JPEG**: 有損壓縮，品質 95%，檔案較小，適合最終輸出

## 輸出結構

```
output/
└── 013大安/
    ├── page_001.png
    ├── page_002.png
    ├── page_003.png
    └── ...
```

## 品質最佳化技術

1. **高解析度渲染**: 使用自訂 DPI 進行高品質渲染
2. **色彩空間優化**: RGB 色彩空間，確保色彩準確
3. **壓縮最佳化**: PNG 使用等級 6 壓縮，JPEG 使用 95% 品質
4. **無色度抽樣**: JPEG 不進行色度二次抽樣 (subsampling=0)
5. **記憶體優化**: 使用 PIL 進行高效處理

## 範例輸出

```
📄 正在處理: 013大安.pdf
   設定: 300 DPI, 格式: PNG
   縮放倍數: 4.17x
   總頁數: 10
   ✅ 第 1/10 頁: page_001.png (523.4 KB)
   ✅ 第 2/10 頁: page_002.png (487.2 KB)
   ...

✨ 完成！
   輸出目錄: output/013大安
   圖片數量: 10
   總大小: 5.12 MB
   平均大小: 524.8 KB/頁
```

## 注意事項

- PDF 檔案需放在 `input/` 目錄
- 確保有足夠的磁碟空間 (高 DPI 會產生大檔案)
- 處理大型 PDF 需要較多記憶體
- 建議先用低 DPI 測試，確認後再用高 DPI

## 技術細節

- 使用 PyMuPDF (fitz) 進行 PDF 渲染
- 使用 Pillow (PIL) 進行圖片最佳化
- 支援矩陣變換進行高品質縮放
- 自動處理色彩空間轉換

## 授權

本專案為內部工具，僅供學習和開發使用。
