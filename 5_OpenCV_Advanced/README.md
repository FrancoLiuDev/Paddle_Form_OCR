# 專案 5: OpenCV 進階角度檢測

## 📖 簡介

本專案使用 OpenCV 的多種進階技術來檢測和校正圖像的旋轉角度：

- **輪廓檢測法** (`contours`): 使用 `findContours` 和 `minAreaRect` 檢測文檔邊界
- **投影法** (`projection`): 通過計算不同角度的投影方差來找出最佳角度
- **霍夫線條法** (`lines`): 改進版的霍夫變換，使用中位數提高穩定性
- **綜合法** (`combined`): 結合三種方法，根據置信度加權平均

## 🎯 特點

- ✅ **多種檢測方法**: 4 種不同的角度檢測算法
- ✅ **自動選擇最佳**: 綜合模式會根據置信度自動加權
- ✅ **視覺化支援**: 可視化檢測過程中的關鍵特徵
- ✅ **高精度**: 投影法可達到 0.5° 精度
- ✅ **強大的增強**: CLAHE 對比度增強 + 降噪 + 銳化

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 基本使用

```bash
# 使用綜合方法（推薦）
python3 preprocess_opencv.py --input input.jpg --output output.jpg --method combined --verbose

# 使用輪廓檢測
python3 preprocess_opencv.py --input input.jpg --output output.jpg --method contours

# 使用投影法（最精確）
python3 preprocess_opencv.py --input input.jpg --output output.jpg --method projection

# 使用霍夫線條
python3 preprocess_opencv.py --input input.jpg --output output.jpg --method lines

# 視覺化檢測過程
python3 preprocess_opencv.py --input input.jpg --output output.jpg --method lines --visualize debug.jpg
```

## 🔧 方法說明

### 1. 輪廓檢測法 (contours)

**原理**:
- 二值化圖像
- 尋找所有輪廓
- 對最大輪廓計算最小外接矩形
- 從矩形角度推算旋轉角度

**優點**:
- 對有明確邊界的文檔效果好
- 速度快
- 適合掃描件

**缺點**:
- 需要清晰的邊界
- 對噪聲敏感

**置信度**: 基於輪廓面積與圖像面積的比例

### 2. 投影法 (projection)

**原理**:
- 測試多個角度（-10° 到 10°，步長 0.5°）
- 對每個角度計算水平投影
- 選擇投影方差最大的角度（文字行最清晰）

**優點**:
- 精度最高（0.5° 步長）
- 對文字行清晰的文檔效果極好
- 不依賴邊界

**缺點**:
- 速度較慢（需要測試多個角度）
- 角度範圍有限（-10° 到 10°）

**置信度**: 基於最大方差與平均方差的比值

### 3. 霍夫線條法 (lines)

**原理**:
- Canny 邊緣檢測
- HoughLinesP 檢測線段
- 計算每條線的角度
- 使用中位數作為最終角度（比平均值更穩定）

**優點**:
- 對線條清晰的文檔效果好
- 適合表格
- 改進版使用中位數，更穩定

**缺點**:
- 需要明顯的線條
- 參數需要調整

**置信度**: 基於角度的一致性（標準差越小越好）

### 4. 綜合法 (combined)

**原理**:
- 同時使用三種方法
- 根據各方法的置信度進行加權平均
- 取得最穩定的結果

**優點**:
- 最穩定
- 適用範圍最廣
- 自動選擇最可靠的方法

**缺點**:
- 速度最慢（需要運行三種方法）

## 📊 方法比較

| 方法 | 精度 | 速度 | 適用場景 | 推薦度 |
|------|------|------|----------|--------|
| 輪廓檢測 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 掃描件、有邊界的文檔 | ⭐⭐⭐ |
| 投影法 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 文字行清晰的文檔 | ⭐⭐⭐⭐ |
| 霍夫線條 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 表格、線條清晰 | ⭐⭐⭐⭐ |
| 綜合法 | ⭐⭐⭐⭐⭐ | ⭐⭐ | 所有類型 | ⭐⭐⭐⭐⭐ |

## 🎨 圖像增強流程

1. **降噪**: `fastNlMeansDenoisingColored` 非局部均值降噪
2. **對比度增強**: CLAHE (自適應直方圖均衡化)
3. **銳化**: 使用卷積核銳化邊緣

## 💡 使用建議

- **表格掃描件**: 使用 `lines` 或 `combined`
- **普通文檔**: 使用 `projection` 或 `combined`
- **不確定類型**: 使用 `combined`（最保險）
- **需要速度**: 使用 `contours`
- **需要精度**: 使用 `projection` 或 `combined`

## 🔍 輸出說明

### Verbose 模式輸出

```
=== OpenCV 進階角度檢測 (combined) ===

=== 方法 1: 輪廓檢測 ===
  輪廓數量: 42
  最大輪廓面積: 589234
  檢測角度: -1.23°
  置信度: 95.42%

=== 方法 2: 投影法 ===
  測試角度範圍: -10.0° 到 9.5°
  步長: 0.5°
  最佳角度: -0.97°
  最大方差: 123456
  置信度: 72.18%

=== 方法 3: 霍夫線條 ===
  檢測到線條: 187
  角度中位數: -1.10°
  角度標準差: 5.23°
  置信度: 88.38%

=== 綜合結果 ===
  輪廓: -1.23° (權重: 95.42%)
  投影: -0.97° (權重: 72.18%)
  線條: -1.10° (權重: 88.38%)
  最終角度: -1.11°
  最終置信度: 85.33%
```

## 🆚 與其他專案比較

| 專案 | 主要技術 | 特點 |
|------|---------|------|
| 專案 1 | 霍夫線條 | 快速，4 個固定角度 |
| 專案 2 | PCA | 高精度，統計方法 |
| 專案 3 | 深度學習 | 可訓練，需要模型 |
| 專案 4 | OCR 整合 | 完整流程 |
| **專案 5** | **OpenCV 多方法** | **綜合、靈活、精確** |

## 🛠 進階參數調整

如需針對特定場景優化，可以修改程式碼中的參數：

### 輪廓檢測
```python
# 二值化閾值
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
```

### 投影法
```python
# 角度範圍和步長
angles = np.arange(-10, 10, 0.5)  # 可調整範圍和精度
```

### 霍夫線條
```python
# HoughLinesP 參數
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 
                       threshold=100,      # 可降低以檢測更多線條
                       minLineLength=100,  # 最小線長
                       maxLineGap=10)      # 最大間隙
```

## 📝 範例

### Python API 使用

```python
import cv2
from preprocess_opencv import preprocess_image, detect_angle_combined

# 讀取圖像
image = cv2.imread('input.jpg')

# 檢測角度
angle, confidence = detect_angle_combined(image, verbose=True)
print(f"檢測角度: {angle:.2f}°, 置信度: {confidence:.2%}")

# 完整預處理
processed, angle = preprocess_image(image, method='combined', verbose=True)

# 保存結果
cv2.imwrite('output.jpg', processed)
```

## 🤝 貢獻

歡迎提出建議或改進！

## 📄 授權

MIT License
