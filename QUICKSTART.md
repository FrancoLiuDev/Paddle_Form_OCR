# 快速開始指南

## ✅ 專案已完成設置

所有 4 個專案已經創建完成，每個專案都是獨立的，可以單獨使用。

## 📁 專案結構

```
Paddle_Form_OCR_Projects/
├── 1_Hough_Line_Detection/     ← 霍夫直線檢測（最快）
│   ├── preprocess_hough.py
│   ├── requirements.txt
│   └── README.md
│
├── 2_Scikit_Learn_PCA/         ← PCA 分析（任意角度）
│   ├── preprocess_pca.py
│   ├── requirements.txt
│   └── README.md
│
├── 3_MobileNetV3_DL/           ← 深度學習（最精確）
│   ├── rotation_detector.py
│   ├── preprocess_dl.py
│   ├── train.py
│   ├── requirements.txt
│   └── README.md
│
├── 4_OCR_Recognition/          ← OCR 識別（整合方案）
│   ├── ocr_parser.py
│   ├── requirements.txt
│   └── README.md
│
├── test.jpg                    ← 測試圖像
├── README.md                   ← 主說明文件
├── COMPARISON.md               ← 詳細比較
└── SETUP.sh                    ← 設置腳本
```

## 🚀 立即測試

### 測試 1: 霍夫直線檢測（最快）

```bash
cd 1_Hough_Line_Detection
pip install -r requirements.txt
python3 preprocess_hough.py --input ../test.jpg --output result.jpg --verbose
```

### 測試 2: PCA 分析（推薦）

```bash
cd 2_Scikit_Learn_PCA
pip install -r requirements.txt
python3 preprocess_pca.py --input ../test.jpg --output result.jpg --verbose
```

### 測試 3: OCR 識別

```bash
cd 4_OCR_Recognition
pip install -r requirements.txt

# 基本 OCR
python3 ocr_parser.py --image ../test.jpg --output result.json

# OCR + PCA 預處理
python3 ocr_parser.py --image ../test.jpg --output result.json \
    --preprocess --method pca --verbose
```

## 📊 專案選擇

**不知道選哪個？看這裡：**

| 你的需求 | 推薦專案 | 理由 |
|---------|---------|------|
| 表格/表單文檔 | 專案 1 | 速度快，表格線檢測準確 |
| 純文字任意角度 | 專案 2 | 不限角度，效果穩定 |
| 需要最高精度 | 專案 3 | 可訓練，精度最高 |
| 完整 OCR 流程 | 專案 4 | 整合所有方法 |
| 快速測試原型 | 專案 2 | 平衡速度和精度 |

## 🔧 使用技巧

### 1. 比較不同方法的效果

```bash
cd 4_OCR_Recognition

# 不預處理
python3 ocr_parser.py --image ../test.jpg --output result_none.json

# 霍夫直線
python3 ocr_parser.py --image ../test.jpg --output result_hough.json \
    --preprocess --method hough

# PCA
python3 ocr_parser.py --image ../test.jpg --output result_pca.json \
    --preprocess --method pca

# 比較結果
cat result_*.json | grep "total_blocks"
```

### 2. 可視化檢測結果

```bash
cd 1_Hough_Line_Detection

# 顯示檢測到的線條（紅色標記）
python3 preprocess_hough.py --input ../test.jpg --output result.jpg \
    --show-lines --verbose
```

### 3. 高敏感度識別

```bash
cd 4_OCR_Recognition

# 高敏感度模式（識別更多文字）
python3 ocr_parser.py --image ../test.jpg --output result.json \
    --high-sensitivity --verbose
```

### 4. 完整流程（推薦）

```bash
cd 4_OCR_Recognition

# 預處理 + 高敏感度 + 可視化
python3 ocr_parser.py --image ../test.jpg --output result.json \
    --preprocess --method pca \
    --high-sensitivity \
    --visualize output.jpg \
    --verbose
```

## 📖 詳細文檔

- **README.md** - 主要說明文件
- **COMPARISON.md** - 詳細比較 3 種預處理方法
- **各專案的 README.md** - 各專案的詳細說明
- **SETUP.sh** - 快速查看專案資訊

查看專案資訊：
```bash
./SETUP.sh
```

## 🎯 下一步

### 初學者
1. 從專案 2（PCA）開始測試
2. 嘗試不同的測試圖像
3. 比較有/無預處理的差異

### 進階使用
1. 調整各專案的參數
2. 整合到現有系統
3. 根據實際場景選擇最佳方案

### 專業開發
1. 準備訓練數據
2. 訓練專案 3 的深度學習模型
3. 建立完整的生產部署流程

## ❓ 常見問題

**Q: 哪個方法最好？**
A: 取決於你的場景。表格用霍夫，純文字用 PCA，需要極高精度用深度學習。

**Q: 可以同時安裝所有依賴嗎？**
A: 可以，但建議分開安裝。每個專案都是獨立的。

**Q: PCA 結果不準確怎麼辦？**
A: 可以嘗試調整 Canny 邊緣檢測參數，或使用深度學習方法。

**Q: 如何整合到我的專案？**
A: 複製對應專案的 Python 檔案到你的專案，然後 import 使用。

**Q: 需要 GPU 嗎？**
A: 只有專案 3（深度學習）推薦使用 GPU，其他都可以用 CPU。

## 📞 獲取幫助

1. 查看各專案的 README.md
2. 閱讀 COMPARISON.md 瞭解詳細比較
3. 使用 `--verbose` 參數查看詳細輸出
4. 使用 `--help` 查看命令列參數

## 🎉 開始使用

現在你可以開始測試了！建議從以下命令開始：

```bash
cd 2_Scikit_Learn_PCA
pip install -r requirements.txt
python3 preprocess_pca.py --input ../test.jpg --output result.jpg --verbose
```

祝使用順利！🚀
