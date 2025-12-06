# 專案 3: MobileNetV3 深度學習預處理

## 簡介

使用 MobileNetV3 深度學習模型來預測圖像的旋轉角度，支援任意角度的精確預測。

## 技術原理

### 1. 模型架構

使用輕量級的 MobileNetV3-Small 作為特徵提取器

### 2. 訓練方法

- 數據增強：隨機旋轉、縮放、翻轉
- 損失函數：MSE 損失 + 角度連續性約束
- 優化器：AdamW

### 3. 推理流程

輸入圖像 → 特徵提取 → 角度預測 → 圖像旋轉

## 優點

- ✅ 最高精確度
- ✅ 支援任意角度預測
- ✅ 可通過訓練適應特定場景
- ✅ 對噪點和複雜背景更魯棒

## 缺點

- ❌ 需要訓練數據
- ❌ 需要 GPU 加速（推薦）
- ❌ 模型檔案較大
- ❌ 推理速度較慢

## 使用方法

```bash
# 安裝依賴
pip install -r requirements.txt

# 訓練模型
python3 train.py --data-dir ./training_data --epochs 50 --batch-size 32

# 推理預測
python3 preprocess_dl.py --input image.jpg --output processed.jpg --model model.pth --verbose

# 使用 PCA 作為後備方案（無模型時）
python3 preprocess_dl.py --input image.jpg --output processed.jpg --verbose
```

## 訓練數據準備

```
training_data/
├── images/
│   ├── img001.jpg
│   ├── img002.jpg
│   └── ...
└── annotations.json  # 格式: {"img001.jpg": 0, "img002.jpg": 15.5, ...}
```

## 適用場景

- 大量相似文檔需要處理
- 需要最高精確度
- 有 GPU 資源可用
- 可以準備訓練數據
