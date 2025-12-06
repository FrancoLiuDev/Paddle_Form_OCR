# 專案 2: Scikit-Learn PCA 預處理

## 簡介

使用主成分分析（PCA）來檢測圖像中文字的主要方向，支援任意角度的旋轉校正。

## 技術原理

### 1. 邊緣檢測

使用 Canny 算法提取圖像中的邊緣點

### 2. PCA 主成分分析

對邊緣點進行 PCA 分析，找出主要方向向量

### 3. 角度計算

根據第一主成分的方向計算旋轉角度

## 優點

- ✅ 支援任意角度檢測（不限於固定角度）
- ✅ 基於統計方法，較為穩健
- ✅ 不依賴明顯的線條特徵

## 缺點

- ❌ 需要額外依賴 scikit-learn
- ❌ 對噪點較敏感
- ❌ 計算速度較慢

## 使用方法

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行預處理
python3 preprocess_pca.py --input image.jpg --output processed.jpg --verbose

# 查看詳細分析
python3 preprocess_pca.py --input image.jpg --output processed.jpg --verbose --debug
```

## 適用場景

- 純文字文檔（無表格線）
- 任意角度的文字掃描
- 需要精確角度校正的場景
