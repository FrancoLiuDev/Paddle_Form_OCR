# 快速開始指南

## 第一步：確保有 OCR 結果

```bash
# 如果還沒有 OCR 結果，先執行：
cd ../4_OCR_Recognition
python3 ocr_parser.py --image ../images/fuji.png --output result/result_fuji.json
cd ../5_Text_Extraction
```

## 第二步：使用文字提取工具

### 1. 查看摘要（了解 OCR 結果）

```bash
python3 text_extractor.py --input ../4_OCR_Recognition/result/result_fuji.json --summary
```

### 2. 提取特定資料

```bash
# 提取頁數
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -e pages

# 提取日期
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -e dates

# 提取所有文字
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -e all
```

### 3. 搜尋特定文字

```bash
# 關鍵字搜尋
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -k "系统"

# 正則表達式搜尋
python3 text_extractor.py -i ../4_OCR_Recognition/result/result_fuji.json -r "\d+\s*[頁页]"
```

### 4. 輸出結果到檔案

```bash
python3 text_extractor.py \
    -i ../4_OCR_Recognition/result/result_fuji.json \
    -e pages \
    -o output.json
```

## 第三步：在 Python 程式中使用

```python
from text_extractor import TextExtractor

# 初始化
extractor = TextExtractor('result.json', verbose=True)

# 提取頁數
pages = extractor.extract_pages()
print(f"總頁數: {pages['max_pages']}")

# 關鍵字搜尋
results = extractor.extract_by_keyword('系統')

# 正則表達式
results = extractor.extract_by_regex(r'\d+\s*頁')
```

## 常用命令速查

```bash
# 查看幫助
python3 text_extractor.py --help

# 執行 Python 範例
python3 example_extract.py

# 組合多種提取
python3 text_extractor.py -i result.json --summary -e pages -k "系统" -o output.json
```

## 下一步

閱讀完整文件：`README.md`
