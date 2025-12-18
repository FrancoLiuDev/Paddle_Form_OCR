# 13_Skew_Angle_Detection

圖片傾斜角度檢測模組，基於 [deskew](https://github.com/sbrunner/deskew) 函式庫封裝。

## 功能特點

- 🎯 **精確檢測**: 使用 Hough Line Transform 演算法檢測圖片傾斜角度
- 📦 **模組化設計**: 提供類別和函數兩種使用方式
- 🔧 **可自訂參數**: 支援調整 sigma、num_peaks 等檢測參數
- 🚀 **批次處理**: 支援一次檢測多張圖片
- 🛡️ **錯誤處理**: 完善的檔案驗證和異常處理

## 安裝依賴

```bash
pip install opencv-python numpy deskew scikit-image
```

## 使用方法

### 方法 1: 使用簡單函數

```python
from skew_detector import detect_skew_angle

# 檢測單張圖片
angle = detect_skew_angle('path/to/image.png')
if angle is not None:
    print(f"傾斜角度: {angle:.2f}°")
```

### 方法 2: 使用 SkewDetector 類別

```python
from skew_detector import SkewDetector

# 建立檢測器實例（可自訂參數）
detector = SkewDetector(
    sigma=3.0,       # 高斯模糊的 sigma 值
    num_peaks=20,    # Hough transform 的峰值數量
    min_angle=-45,   # 最小角度
    max_angle=45     # 最大角度
)

# 檢測單張圖片
angle = detector.detect_angle_from_file('image.png')

# 批次檢測多張圖片
image_paths = ['img1.png', 'img2.png', 'img3.png']
results = detector.detect_batch(image_paths, verbose=True)

for path, angle in results.items():
    if angle is not None:
        print(f"{path}: {angle:.2f}°")
```

### 方法 3: 使用命令列

```bash
# 檢測單張圖片
python3 skew_detector.py path/to/image.png

# 檢測多張圖片
python3 skew_detector.py image1.png image2.png image3.png
```

## 測試

```bash
# 運行測試腳本
python3 test_skew_detector.py
```

測試腳本包含：
- ✓ 單張圖片檢測
- ✓ 類別方法測試
- ✓ 批次處理測試
- ✓ 不同參數設定測試

## API 參考

### `detect_skew_angle(image_path)`

最簡單的使用方式，適合快速檢測。

**參數:**
- `image_path` (str): 圖片檔案路徑

**返回:**
- `float | None`: 傾斜角度（度），如果無法檢測則返回 None

### `SkewDetector`

提供更多控制和批次處理能力的類別。

#### `__init__(sigma, num_peaks, min_angle, max_angle, min_deviation)`

**參數:**
- `sigma` (float, 預設=3.0): 高斯模糊的標準差
- `num_peaks` (int, 預設=20): Hough transform 檢測的峰值數量
- `min_angle` (float, 預設=-45): 最小傾斜角度
- `max_angle` (float, 預設=45): 最大傾斜角度
- `min_deviation` (float, 預設=0.0): 最小偏差閾值

#### `detect_angle(image, grayscale=True)`

從 numpy 陣列檢測傾斜角度。

**參數:**
- `image` (np.ndarray): 輸入圖片
- `grayscale` (bool, 預設=True): 是否為灰階圖片

**返回:**
- `float | None`: 傾斜角度

#### `detect_angle_from_file(image_path)`

從檔案路徑檢測傾斜角度。

**參數:**
- `image_path` (str | Path): 圖片檔案路徑

**返回:**
- `float | None`: 傾斜角度

#### `detect_batch(image_paths, verbose=False)`

批次檢測多張圖片。

**參數:**
- `image_paths` (list[str | Path]): 圖片檔案路徑列表
- `verbose` (bool, 預設=False): 是否顯示進度

**返回:**
- `dict[str, float | None]`: 檔案路徑到傾斜角度的映射

## 演算法說明

檢測流程：

1. **邊緣檢測**: 使用 Canny 演算法檢測圖片邊緣
2. **霍夫轉換**: 使用 Hough Line Transform 找出圖片中的直線
3. **角度計算**: 基於檢測到的直線計算整體傾斜角度
4. **結果輸出**: 返回以度為單位的傾斜角度

## 測試結果

實測結果（來自 test_skew_detector.py）：

| 圖片 | 檢測角度 |
|------|---------|
| fuji45.png | 20.00° |
| fuji3.png | -12.00° |
| page_014.png | -11.00° |
| fuji10.png | 7.00° |
| fuji0.png | 1.00° |

## 參數調校建議

### sigma (高斯模糊)
- **小值 (1.0)**: 保留更多細節，適合高解析度圖片
- **中值 (3.0)**: 預設值，適合一般用途
- **大值 (5.0)**: 去除更多雜訊，適合低品質圖片

### num_peaks (峰值數量)
- **小值 (10)**: 速度較快，但可能漏掉特徵
- **中值 (20)**: 預設值，平衡速度和準確度
- **大值 (40)**: 更準確，但速度較慢

## 整合範例

整合到現有 OCR 管線：

```python
from skew_detector import SkewDetector
import cv2

detector = SkewDetector()

# 檢測角度
image_path = "input.png"
angle = detector.detect_angle_from_file(image_path)

if angle is not None and abs(angle) > 1.0:  # 超過 1 度才校正
    # 讀取圖片
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    # 旋轉矩陣
    rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
    
    # 應用旋轉
    rotated = cv2.warpAffine(
        image, 
        rotation_matrix, 
        (width, height),
        borderValue=(255, 255, 255)
    )
    
    # 儲存校正後的圖片
    cv2.imwrite("output.png", rotated)
    print(f"已校正角度: {angle:.2f}°")
```

## 授權

本模組基於 [deskew](https://github.com/sbrunner/deskew) 函式庫 (MIT License)。

## 相關連結

- [deskew GitHub](https://github.com/sbrunner/deskew)
- [OpenCV 文件](https://docs.opencv.org/)
- [scikit-image](https://scikit-image.org/)
