# 專案 1: 霍夫直線檢測預處理

## 簡介
使用霍夫變換（Hough Transform）檢測圖像中的線條方向，並根據線條角度判斷圖像需要旋轉的方向。

## 技術原理

### 1. 邊緣檢測
使用 Canny 算法檢測圖像邊緣

### 2. 霍夫直線檢測
使用 HoughLinesP 檢測圖像中的直線，並分類為：
- 水平線（0°）
- 45° 斜線
- 垂直線（90°）
- 135° 斜線

### 3. 角度評分
根據各角度線條數量和文本投影方差計算得分，選擇最佳旋轉角度

## 優點
- ✅ 不需要額外依賴（只需 OpenCV）
- ✅ 速度快
- ✅ 對有表格線的文檔效果好

## 缺點
- ❌ 只能檢測固定角度（0°, 45°, 90°, 135°）
- ❌ 依賴明顯的線條特徵
- ❌ 對純文字圖像效果較差

## 使用方法

```bash
# 安裝依賴
pip install opencv-python numpy

# 運行預處理
python3 preprocess_hough.py --input image.jpg --output processed.jpg --verbose

# 可視化線條檢測
python3 preprocess_hough.py --input image.jpg --output processed.jpg --show-lines --verbose
```

## 適用場景
- 表單掃描（有表格線）
- 文檔掃描（有明顯結構）
- 需要快速處理的場景
