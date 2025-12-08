# 全形轉半形功能說明

## 功能概述

OCR 識別器現在支援自動將全形字符轉換為半形字符，提高資料的一致性和可用性。

## 轉換範圍

### 1. 全形數字 → 半形數字
```
１２３４５６７８９０ → 1234567890
```

### 2. 全形英文 → 半形英文
```
ＡＢＣＤＥＦＧ → ABCDEFG
ａｂｃｄｅｆｇ → abcdefg
```

### 3. 全形標點符號 → 半形標點符號
```
：；，。！？ → :;,.!?
（）［］｛｝ → ()[]{}
```

### 4. 全形特殊符號 → 半形特殊符號
```
＠＃＄％＾＆＊ → @#$%^&*
＋－＝／＼ → +-=/\
```

### 5. 全形空格 → 半形空格
```
全形空格（U+3000） → 半形空格（U+0020）
```

## 實際應用範例

### 範例 1: 頁數資料
```
OCR 識別: １２５０頁
轉換後:   1250頁
```

### 範例 2: 型號資料
```
OCR 識別: Ｃ３２５／３２８
轉換後:   C325/328
```

### 範例 3: 序號資料
```
OCR 識別: ＮＣ７００３６７７
轉換後:   NC7003677
```

## 使用方式

### 1. Python API

```python
from ocr_parser import OCRParser

# 啟用全形轉半形（預設）
parser = OCRParser(convert_fullwidth=True)
result = parser.recognize('image.png')

# 停用全形轉半形
parser = OCRParser(convert_fullwidth=False)
result = parser.recognize('image.png')
```

### 2. 命令列

```bash
# 啟用全形轉半形（預設行為）
python3 ocr_parser.py --image test.png -o result.json

# 停用全形轉半形
python3 ocr_parser.py --image test.png -o result.json --no-convert-fullwidth
```

### 3. 查看轉換記錄

當字符被轉換時，JSON 結果會包含 `original_text` 欄位：

```json
{
  "text_blocks": [
    {
      "text": "1250頁",
      "original_text": "１２５０頁",
      "confidence": 0.948,
      "bbox": [[239, 178], [274, 181], [273, 194], [238, 191]]
    }
  ]
}
```

## 技術細節

### 轉換原理

使用 Unicode 字符碼位轉換：

```python
# 全形字符範圍: U+FF01 ~ U+FF5E
# 半形字符範圍: U+0021 ~ U+007E
# 轉換公式: 半形碼位 = 全形碼位 - 0xFEE0

# 範例
'１' (U+FF11) → '1' (U+0031)
'Ａ' (U+FF21) → 'A' (U+0041)
'（' (U+FF08) → '(' (U+0028)
```

### 特殊處理

- **全形空格**: U+3000 → U+0020
- **中文字符**: 保持不變
- **其他字符**: 保持不變

### 性能影響

- 轉換速度極快（純字串操作）
- 對 OCR 識別速度無影響
- 記憶體開銷可忽略

## 為什麼需要這個功能？

### 1. 資料一致性

OCR 有時會將半形字符識別為全形，導致：
- 數字格式不一致（1234 vs １２３４）
- 程式解析錯誤（正則表達式無法匹配）
- 資料庫查詢失敗

### 2. 後續處理方便

半形字符在程式處理上更標準：
```python
# 半形數字可以直接轉換
int("1250")  # ✅ 成功

# 全形數字無法直接轉換
int("１２５０")  # ❌ ValueError
```

### 3. 儲存空間

半形字符佔用 1 個位元組，全形字符佔用 3 個位元組（UTF-8）

## 測試結果

✅ 全形數字轉換: "１２３４５６７８９０" → "1234567890"
✅ 全形英文轉換: "ＡＢＣＤＥＦＧ" → "ABCDEFG"
✅ 全形符號轉換: "（）［］｛｝" → "()[]{}
✅ 全形標點轉換: "：；，。！？" → ":;,.!?"
✅ 混合測試: "１２５０頁" → "1250頁"

## 注意事項

### 1. 不會轉換中文字符

中文字符本身就是全形，不會被轉換：
```
"總印張數" → "總印張數" (保持不變)
```

### 2. 可以隨時切換

可以在程式中隨時啟用或停用：
```python
parser_on = OCRParser(convert_fullwidth=True)
parser_off = OCRParser(convert_fullwidth=False)
```

### 3. 預設啟用

考慮到大多數情況下都需要標準化資料，預設啟用此功能。

## 相關檔案

- `ocr_parser.py` - 主要程式（已整合轉換功能）
- `test_fullwidth_final.py` - 完整測試程式
- `quick_test.py` - 快速測試

## 更新記錄

- 2024-12-08: 新增全形轉半形功能
  - 新增 `fullwidth_to_halfwidth()` 靜態方法
  - 新增 `convert_fullwidth` 參數
  - 新增 `--no-convert-fullwidth` 命令列選項
  - 記錄原始文字到 `original_text` 欄位
