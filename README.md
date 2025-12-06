# Paddle Form OCR - 5 個獨立專案

這個資料夾包含 5 個獨立的專案，每個專案專注於不同的圖像預處理或 OCR 識別方法。

## 專案結構

```
Paddle_Form_OCR/
├── 1_Hough_Line_Detection/     # 霍夫直線檢測預處理
├── 2_Scikit_Learn_PCA/         # PCA 主成分分析預處理
├── 3_MobileNetV3_DL/           # MobileNetV3 深度學習預處理
├── 4_OCR_Recognition/          # OCR 文字識別（可整合前 3 個專案）
└── 5_OpenCV_Advanced/          # OpenCV 進階多方法角度檢測
```

## 各專案特點對比

| 專案 | 優點 | 缺點 | 適用場景 |
|------|------|------|----------|
| **1. 霍夫直線檢測** | 速度快、無額外依賴 | 僅支援固定角度 | 表格、結構化文檔 |
| **2. PCA 分析** | 任意角度、統計穩健 | 需 sklearn、較慢 | 純文字文檔 |
| **3. 深度學習** | 最高精度、可訓練 | 需 GPU、需訓練數據 | 大量相似文檔 |
| **4. OCR 識別** | 整合方案、靈活 | 依賴 PaddleOCR | 生產環境 |
| **5. OpenCV 進階** | 多方法綜合、精確 | 速度中等 | 通用場景 |

## 快速開始

### 1. 霍夫直線檢測

```bash
cd 1_Hough_Line_Detection
pip install -r requirements.txt
python3 preprocess_hough.py --input ../test.jpg --output result.jpg --verbose
```

### 2. PCA 分析

```bash
cd 2_Scikit_Learn_PCA
pip install -r requirements.txt
python3 preprocess_pca.py --input ../test.jpg --output result.jpg --verbose
```

### 3. 深度學習

```bash
cd 3_MobileNetV3_DL
pip install -r requirements.txt

# 訓練模型（需要準備訓練數據）
python3 train.py --data-dir ./training_data --epochs 50

# 推理預測
python3 preprocess_dl.py --input ../test.jpg --output result.jpg --model model.pth --verbose
```

### 4. OCR 識別

```bash
cd 4_OCR_Recognition
pip install -r requirements.txt

# 基本 OCR
python3 ocr_parser.py --image test.jpg --output result.json

# 使用 PCA 預處理
python3 ocr_parser.py --image test.jpg --output result.json --preprocess --method pca --verbose

# 完整流程（預處理 + 高敏感度 + 可視化）
python3 ocr_parser.py --image test.jpg --output result.json \
    --preprocess --method pca --high-sensitivity \
    --visualize output.jpg --verbose
```

### 5. OpenCV 進階

```bash
cd 5_OpenCV_Advanced
pip install -r requirements.txt

# 使用輪廓檢測
python3 preprocess_opencv.py --input ../test.jpg --output result.jpg --method contours --verbose

# 使用投影法（最精確）
python3 preprocess_opencv.py --input ../test.jpg --output result.jpg --method projection --verbose

# 使用霍夫線條（改進版）
python3 preprocess_opencv.py --input ../test.jpg --output result.jpg --method lines --verbose

# 使用綜合方法（推薦）
python3 preprocess_opencv.py --input ../test.jpg --output result.jpg --method combined --verbose

# 視覺化檢測過程
python3 preprocess_opencv.py --input ../test.jpg --output result.jpg --method lines --visualize debug.jpg
```

## 如何選擇專案

### 場景 1: 快速原型

→ 使用 **專案 1（霍夫直線檢測）**
- 速度最快
- 不需要額外依賴
- 適合初步測試

### 場景 2: 任意角度文檔

→ 使用 **專案 2（PCA）** 或 **專案 5（OpenCV 進階）**
- 支援任意角度
- 不需要訓練
- 適合多樣化文檔
- 專案 5 提供多種方法可選

### 場景 3: 高精度需求

→ 使用 **專案 3（深度學習）** 或 **專案 5（綜合模式）**
- 可通過訓練提升精度
- 適應特定場景
- 專案 5 的綜合模式結合多種方法

### 場景 4: 生產部署

→ 使用 **專案 4（OCR 識別）**
- 整合多種方法
- 完整的 OCR 流程
- 靈活配置

### 場景 5: 通用場景不確定

→ 使用 **專案 5（OpenCV 進階 - 綜合模式）**
- 自動選擇最佳方法
- 根據置信度加權
- 適用範圍最廣

## 整合使用

專案 4 可以整合前面專案的預處理方法：

```bash
# 方法 1: 直接整合（推薦）
cd 4_OCR_Recognition
python3 ocr_parser.py --image test.jpg --preprocess --method pca

# 方法 2: 管道處理
cd 2_Scikit_Learn_PCA
python3 preprocess_pca.py --input test.jpg --output preprocessed.jpg

cd ../4_OCR_Recognition
python3 ocr_parser.py --image ../2_Scikit_Learn_PCA/preprocessed.jpg --output result.json
```

## 開發與測試

### 測試單一專案

```bash
# 測試霍夫直線檢測
cd 1_Hough_Line_Detection
python3 preprocess_hough.py --input test.jpg --output result1.jpg --show-lines --verbose

# 測試 PCA
cd ../2_Scikit_Learn_PCA
python3 preprocess_pca.py --input test.jpg --output result2.jpg --debug --verbose

# 比較結果
# 查看 result1.jpg 和 result2.jpg 的差異
```

### 比較不同方法

```bash
cd 4_OCR_Recognition

# 不使用預處理
python3 ocr_parser.py --image test.jpg --output result_none.json

# 使用霍夫直線檢測
python3 ocr_parser.py --image test.jpg --output result_hough.json --preprocess --method hough

# 使用 PCA
python3 ocr_parser.py --image test.jpg --output result_pca.json --preprocess --method pca

# 比較結果
cat result_*.json | grep "total_blocks"
```

## 依賴關係

### 共通依賴
- Python >= 3.7
- OpenCV >= 4.5.0
- NumPy >= 1.19.0

### 特定依賴
- 專案 2: scikit-learn >= 1.0.0
- 專案 3: PyTorch >= 1.9.0, torchvision >= 0.10.0
- 專案 4: PaddleOCR >= 2.6.0

## 授權

請參考各專案的 LICENSE 檔案
