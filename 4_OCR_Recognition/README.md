# 專案 4: OCR 表單識別

## 簡介

使用 PaddleOCR 進行表單文字識別和欄位提取，可整合前面三個預處理專案的任一方法。

## 功能特點

### 1. OCR 文字識別

使用 PaddleOCR 離線引擎進行高精度文字識別

### 2. 表單解析

自動識別和提取表單欄位

### 3. 預處理整合

可選擇整合以下預處理方法：
- 霍夫直線檢測（快速、適合表格）
- PCA 分析（任意角度、適合純文字）
- MobileNetV3（最高精度、需要訓練）

### 4. 結果可視化

生成標註了識別結果的圖像

## 使用方法

```bash
# 安裝依賴
pip install -r requirements.txt

# 基本 OCR 識別
python3 ocr_parser.py --image input.jpg --output result.json

# 使用預處理（自動選擇最佳方法）
python3 ocr_parser.py --image input.jpg --output result.json --preprocess

# 指定預處理方法
python3 ocr_parser.py --image input.jpg --output result.json --preprocess --method hough
python3 ocr_parser.py --image input.jpg --output result.json --preprocess --method pca
python3 ocr_parser.py --image input.jpg --output result.json --preprocess --method dl --model model.pth

# 高敏感度模式（降低檢測閾值）
python3 ocr_parser.py --image input.jpg --output result.json --high-sensitivity

# 可視化結果
python3 ocr_parser.py --image input.jpg --output result.json --visualize output.jpg

# 完整示例
python3 ocr_parser.py --image input.jpg --output result.json \
    --preprocess --method pca --high-sensitivity \
    --visualize output.jpg --verbose
```

## 整合其他預處理專案

### 方法 1: 複製模組

將預處理專案的 Python 檔案複製到此目錄：

```bash
# 使用霍夫直線檢測
cp ../1_Hough_Line_Detection/preprocess_hough.py ./

# 使用 PCA
cp ../2_Scikit_Learn_PCA/preprocess_pca.py ./

# 使用深度學習
cp ../3_MobileNetV3_DL/*.py ./
```

### 方法 2: 獨立預處理

先使用預處理專案處理圖像，再進行 OCR：

```bash
# 步驟 1: 預處理
cd ../2_Scikit_Learn_PCA
python3 preprocess_pca.py --input ../4_OCR_Recognition/input.jpg \
    --output ../4_OCR_Recognition/preprocessed.jpg

# 步驟 2: OCR 識別
cd ../4_OCR_Recognition
python3 ocr_parser.py --image preprocessed.jpg --output result.json
```

## 輸出格式

```json
{
  "rotation_angle": 15.5,
  "preprocessing_method": "pca",
  "text_blocks": [
    {
      "text": "識別的文字",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
      "angle": 0.0
    }
  ],
  "fields": {
    "name": "張三",
    "date": "2024-01-01"
  }
}
```

## 適用場景

- 表單識別和數據提取
- 文檔數位化
- 自動化資料處理
- 整合多種預處理方法的生產環境
