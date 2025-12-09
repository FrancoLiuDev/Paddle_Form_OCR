# Excel 解析器

這是一個 Python 工具，用於解析和分析 Excel 檔案（.xlsx 格式）。

## 功能特色

### 1. 檔案資訊
- 檔案大小
- 修改時間
- 工作表數量

### 2. 工作表分析
- 自動偵測標題行
- 讀取所有儲存格資料
- 儲存格類型識別（數字、文字、日期、公式等）
- 合併儲存格檢測

### 3. 統計資訊
- 總儲存格數
- 空白儲存格數
- 數值儲存格數（含統計：總和、平均、最大、最小）
- 文字儲存格數
- 公式儲存格數
- 日期儲存格數
- 資料填充率

## 安裝

```bash
cd 7_Excel_Parser
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python3 excel_parser.py <excel_file_path>
```

### 範例

```bash
# 解析 example.xlsx
python3 excel_parser.py ../6_Desktop_App/input/example.xlsx

# 或使用測試腳本
python3 test_parser.py
```

## 輸出格式

輸出為 JSON 格式，包含：

```json
{
  "success": true,
  "file_info": {
    "path": "檔案路徑",
    "name": "檔案名稱",
    "size": 12345,
    "size_formatted": "12.05 KB",
    "modified": "2025-12-09 10:30:00"
  },
  "workbook_info": {
    "total_sheets": 3,
    "sheet_names": ["Sheet1", "Sheet2", "Sheet3"],
    "active_sheet": "Sheet1"
  },
  "sheets": [
    {
      "name": "Sheet1",
      "range": {
        "min_row": 1,
        "max_row": 100,
        "min_column": 1,
        "max_column": 10,
        "total_rows": 100,
        "total_columns": 10
      },
      "headers": ["欄位1", "欄位2", ...],
      "data": [
        [
          {
            "value": "資料",
            "type": "string",
            "coordinate": "A1",
            "formatted": "資料"
          },
          ...
        ],
        ...
      ],
      "statistics": {
        "total_cells": 1000,
        "empty_cells": 50,
        "numeric_cells": 300,
        "text_cells": 650,
        "formula_cells": 10,
        "fill_rate": 95.0,
        "numeric_stats": {
          "count": 300,
          "sum": 15000,
          "average": 50,
          "min": 1,
          "max": 999
        }
      },
      "merged_cells": ["A1:B1", "C3:D4"],
      "has_more": false
    }
  ]
}
```

## 特殊功能

### 1. 儲存格類型識別
- `empty`: 空白
- `number`: 數字
- `string`: 文字
- `datetime`: 日期時間
- `boolean`: 布林值
- `formula`: 公式（會同時顯示公式內容）

### 2. 超連結支援
如果儲存格含有超連結，會在輸出中顯示：
```json
{
  "value": "點擊這裡",
  "hyperlink": "https://example.com"
}
```

### 3. 資料限制
- 為避免記憶體問題，每個工作表最多讀取 1000 行
- 如果超過限制，`has_more` 欄位會設為 `true`

## 錯誤處理

如果解析失敗，會回傳：

```json
{
  "success": false,
  "error": "錯誤訊息",
  "error_type": "Exception",
  "file_path": "檔案路徑"
}
```

## 系統需求

- Python 3.7+
- openpyxl 3.1.0+

## 整合

此解析器可以整合到其他專案中：

```python
from excel_parser import ExcelParser

parser = ExcelParser("path/to/file.xlsx")
result = parser.parse()

if result["success"]:
    print(f"共有 {result['workbook_info']['total_sheets']} 個工作表")
    for sheet in result["sheets"]:
        print(f"工作表: {sheet['name']}")
        print(f"資料範圍: {sheet['range']['total_rows']}x{sheet['range']['total_columns']}")
else:
    print(f"解析失敗: {result['error']}")
```

## 授權

此專案為內部使用，未指定公開授權。
