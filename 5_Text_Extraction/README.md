# 文字提取專案 (5_Text_Extraction)

## 專案說明

這個專案專門用於從 `4_OCR_Recognition` 的 OCR 識別結果中提取特定的文字和數據。

## 功能特色

### 📋 基礎提取功能
- ✅ 關鍵字搜尋
- ✅ 正則表達式匹配
- ✅ 數字提取
- ✅ 位置定位提取

### 🎯 專用提取功能
- ✅ 頁數提取（如：1250頁）
- ✅ 計數提取（如：列印次數、張數）
- ✅ 日期提取
- ✅ 時間提取
- ✅ ID/編號提取
- ✅ 全文提取

### 🔧 高級功能
- ✅ 多條件組合篩選
- ✅ 信心度過濾
- ✅ 位置範圍過濾
- ✅ OCR 結果摘要

## 安裝需求

```bash
# 無需額外安裝，使用 Python 標準庫即可
python3 --version  # 需要 Python 3.6+
```

## 快速開始

### 1. 基本使用

```bash
# 查看摘要
python3 text_extractor.py --input ../4_OCR_Recognition/result/result_fuji.json --summary

# 提取頁數資訊
python3 text_extractor.py --input ../4_OCR_Recognition/result/result_fuji.json --extract pages

# 提取所有文字
python3 text_extractor.py --input ../4_OCR_Recognition/result/result_fuji.json --extract all
```

### 2. 關鍵字搜尋

```bash
# 搜尋包含「系統」的文字
python3 text_extractor.py --input result.json --keyword "系統"

# 搜尋包含「頁」的文字
python3 text_extractor.py --input result.json --keyword "頁"
```

### 3. 正則表達式搜尋

```bash
# 搜尋日期格式 (YYYY/MM/DD)
python3 text_extractor.py --input result.json --regex "\d{4}/\d{2}/\d{2}"

# 搜尋數字+頁
python3 text_extractor.py --input result.json --regex "\d+\s*[頁页]"

# 搜尋 4 位數字
python3 text_extractor.py --input result.json --regex "\d{4}"
```

### 4. 提取特定類型資料

```bash
# 提取頁數
python3 text_extractor.py -i result.json -e pages

# 提取日期
python3 text_extractor.py -i result.json -e dates

# 提取時間
python3 text_extractor.py -i result.json -e times

# 提取 ID/編號
python3 text_extractor.py -i result.json -e ids

# 提取計數（次數、張數等）
python3 text_extractor.py -i result.json -e counts
```

### 5. 輸出到檔案

```bash
# 提取結果儲存為 JSON
python3 text_extractor.py -i result.json -e pages -o output.json

# 多種提取組合
python3 text_extractor.py -i result.json --summary --extract pages --keyword "系統" -o output.json
```

## 使用範例

### 範例 1：提取「1250頁」

```bash
python3 text_extractor.py \
    --input ../4_OCR_Recognition/result/result_fuji.json \
    --extract pages \
    --verbose
```

輸出：
```
找到 3 個頁數資訊:
  • 1250页              → 1250 頁 (信心度: 94.8%)
  • 294页               →  294 頁 (信心度: 99.5%)
  • 95 6 页             →   95 頁 (信心度: 81.5%)

📊 最大頁數: 1250 頁
```

### 範例 2：搜尋系統設定相關文字

```bash
python3 text_extractor.py \
    --input ../4_OCR_Recognition/result/result_fuji.json \
    --keyword "系統" \
    --min-confidence 0.8
```

### 範例 3：提取日期和時間

```bash
python3 text_extractor.py \
    --input ../4_OCR_Recognition/result/result_fuji.json \
    --extract dates
```

### 範例 4：Python 腳本使用

```python
from text_extractor import TextExtractor

# 初始化
extractor = TextExtractor('result.json', verbose=True)

# 提取頁數
pages = extractor.extract_pages()
print(f"總頁數: {pages['max_pages']}")

# 提取日期
dates = extractor.extract_dates()
print(f"找到 {len(dates)} 個日期")

# 關鍵字搜尋
results = extractor.extract_by_keyword('系統')
for r in results:
    print(f"文字: {r['text']}, 信心度: {r['confidence']}")

# 正則表達式
results = extractor.extract_by_regex(r'\d+\s*頁')
for r in results:
    print(f"匹配: {r['matches']}")

# 取得摘要
summary = extractor.get_summary()
print(f"總文字區塊: {summary['total_blocks']}")
print(f"平均信心度: {summary['avg_confidence']:.2%}")
```

## 完整命令列參數

```bash
python3 text_extractor.py --help
```

| 參數 | 簡寫 | 說明 |
|------|------|------|
| `--input` | `-i` | OCR 結果 JSON 檔案路徑（必填） |
| `--extract` | `-e` | 提取類型：pages/counts/dates/times/ids/all |
| `--keyword` | `-k` | 搜尋關鍵字 |
| `--regex` | `-r` | 正則表達式模式 |
| `--min-confidence` | | 最低信心度閾值 (0.0-1.0) |
| `--summary` | `-s` | 顯示 OCR 結果摘要 |
| `--output` | `-o` | 輸出結果到 JSON 檔案 |
| `--verbose` | `-v` | 顯示詳細資訊 |

## 提取方法說明

### 1. 頁數提取 (pages)
- 自動識別包含「頁」、「页」、「page」的文字
- 提取數字並找出最大值（通常是總頁數）
- 適用於：文件頁數、列印頁數統計

### 2. 計數提取 (counts)
- 識別包含「次」、「張」等計數單位的文字
- 提取並累加數字
- 適用於：列印次數、影印張數

### 3. 日期提取 (dates)
- 支援多種日期格式：YYYY/MM/DD, YYYY-MM-DD, YYYY年MM月DD日
- 自動識別常見日期模式
- 適用於：文件日期、建立時間

### 4. 時間提取 (times)
- 支援 HH:MM 和 HH:MM:SS 格式
- 適用於：時間戳記、列印時間

### 5. ID 提取 (ids)
- 識別連續的大寫字母+數字組合
- 可指定前綴（如 NC, ID）
- 適用於：序號、機器編號、文件編號

### 6. 全文提取 (all)
- 提取所有文字內容
- 可設定信心度閾值過濾
- 適用於：完整文字匯出

## 進階技巧

### 組合多個條件

```python
from text_extractor import TextExtractor

extractor = TextExtractor('result.json')

# 組合條件：關鍵字 + 信心度 + 位置
results = extractor.extract_with_conditions(
    keyword='頁',
    pattern=r'\d{3,}',      # 至少3位數字
    min_confidence=0.9,     # 信心度 > 90%
    x_range=(200, 300),     # X 座標範圍
    y_range=(100, 200)      # Y 座標範圍
)
```

### 自訂正則表達式

```python
# 提取電話號碼
extractor.extract_by_regex(r'\d{2,4}-\d{6,8}')

# 提取 Email
extractor.extract_by_regex(r'[\w\.-]+@[\w\.-]+\.\w+')

# 提取 IP 位址
extractor.extract_by_regex(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

# 提取金額（含逗號）
extractor.extract_by_regex(r'\d{1,3}(,\d{3})*')
```

## 檔案結構

```
5_Text_Extraction/
├── text_extractor.py       # 主程式
├── README.md              # 說明文件
└── examples/              # 範例目錄
    ├── example_extract.py # Python 使用範例
    └── example_results/   # 範例輸出結果
```

## 與 4_OCR_Recognition 的關係

```
工作流程：
1. 使用 4_OCR_Recognition 進行 OCR 識別
   → 產生 result.json

2. 使用 5_Text_Extraction 提取特定資料
   → 從 result.json 中提取所需的文字和數據

3. 後續處理
   → 將提取的數據用於其他應用
```

範例：
```bash
# 步驟 1: OCR 識別
cd 4_OCR_Recognition
python3 ocr_parser.py --image ../images/fuji.png --output result/result_fuji.json

# 步驟 2: 文字提取
cd ../5_Text_Extraction
python3 text_extractor.py --input ../4_OCR_Recognition/result/result_fuji.json --extract pages

# 步驟 3: 輸出結果
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -e pages -o extracted_data.json
```

## 常見問題

### Q1: 提取的數字不正確？
**A:** 使用 `--min-confidence` 參數過濾低信心度的結果：
```bash
python3 text_extractor.py -i result.json -e pages --min-confidence 0.8
```

### Q2: 找不到特定文字？
**A:** 使用 `--verbose` 查看詳細資訊，或先查看摘要：
```bash
python3 text_extractor.py -i result.json --summary --verbose
```

### Q3: 正則表達式不匹配？
**A:** 檢查編碼和特殊字元，使用原始字串 `r''`：
```python
# 錯誤
pattern = "\d+"  # 反斜線會被轉義

# 正確
pattern = r"\d+"  # 使用原始字串
```

### Q4: 如何提取特定位置的文字？
**A:** 使用 `extract_by_position()` 方法：
```python
results = extractor.extract_by_position(
    x_range=(100, 300),
    y_range=(50, 150)
)
```

## 授權

本專案屬於 Paddle_Form_OCR 專案的一部分。

## 更新日誌

### 2025-12-08
- ✨ 初始版本發布
- ✅ 支援基礎提取功能
- ✅ 支援專用提取功能（頁數、日期、時間等）
- ✅ 支援多條件組合篩選
- ✅ 命令列工具完成
