# OCR 文字圖像生成功能

## 功能說明

新增 `--text-image` 參數，可以將識別到的文字繪製在白色背景上，生成純文字圖像（白底黑字）。

## 使用方法

### 基本用法

```bash
# 生成純文字圖像
python3 ocr_parser.py --image INPUT.png --text-image OUTPUT_TEXT.jpg --verbose
```

### 完整範例

```bash
# 1. 只生成文字圖像
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --text-image result/fuji_text.jpg \
    --verbose

# 2. 同時生成 JSON、可視化和文字圖像
python3 ocr_parser.py \
    --image ../images/fujid.png \
    --output result/fujid.json \
    --visualize result/fujid_visual.jpg \
    --text-image result/fujid_text.jpg \
    --verbose

# 3. 使用預處理 + 生成文字圖像
python3 ocr_parser.py \
    --image ../images/fuji45.png \
    --preprocess \
    --method pca \
    --text-image result/fuji45_text.jpg \
    --verbose
```

## 輸出說明

### 1. 原始圖像 (INPUT)
- 原始掃描或拍攝的文件圖像

### 2. 可視化圖像 (--visualize)
- 在原始圖像上繪製綠色框和識別結果
- 顯示每個文字區塊的位置和信心度

### 3. 純文字圖像 (--text-image) ✨ 新功能
- **白色背景 + 黑色文字**
- 文字位置與原圖相同
- 支援中文顯示（使用系統字體）
- 適合用於：
  - 文字提取和重新排版
  - 對比原始圖像查看識別效果
  - 作為文字識別的中間結果

### 4. JSON 結果 (--output)
- 包含所有文字內容、位置座標、信心度
- 可用於後續處理

## 範例對比

### 測試圖片：fuji.png

```bash
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --output result/result_fuji.json \
    --visualize result/result_fuji_visual.jpg \
    --text-image result/result_fuji_text.jpg \
    --verbose
```

輸出：
- `result_fuji.json` - 204 個文字區塊的完整資料
- `result_fuji_visual.jpg` - 原圖 + 綠色框 + 標註
- `result_fuji_text.jpg` - 白底黑字的純文字圖像 ✨

### 測試圖片：fujid.png (倒轉的圖片)

```bash
python3 ocr_parser.py \
    --image ../images/fujid.png \
    --text-image result/result_fujid_text.jpg \
    --verbose
```

輸出：
- `result_fujid_text.jpg` - 184 個文字區塊，已自動校正方向 ✨

## 技術細節

### 字體支援

程式會自動尋找系統中的中文字體：

**Linux 系統：**
- `/usr/share/fonts/truetype/wqy/wqy-microhei.ttc` (文泉驛微米黑)
- `/usr/share/fonts/truetype/arphic/uming.ttc` (AR PL UMing)
- `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` (思源黑體)
- `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` (DejaVu)

如果找不到字體，會使用預設字體（可能無法正確顯示中文）。

### 依賴套件

- `Pillow` (PIL) - 用於繪製中文字體
- 已經在 requirements.txt 中包含

```bash
pip3 install Pillow
```

## 完整參數列表

```bash
python3 ocr_parser.py --help
```

| 參數 | 簡寫 | 說明 |
|------|------|------|
| `--image` | `-i` | 輸入圖像路徑（必填） |
| `--output` | `-o` | 輸出 JSON 檔案路徑 |
| `--visualize` | `-v` | 可視化輸出路徑（原圖+標註） |
| `--text-image` | `-t` | **純文字圖像輸出路徑（白底黑字）** ✨ |
| `--lang` | | 識別語言（ch/en/ch_en，預設 ch） |
| `--use-gpu` | | 使用 GPU 加速 |
| `--high-sensitivity` | | 高敏感度模式 |
| `--preprocess` | | 啟用預處理 |
| `--method` | | 預處理方法（hough/pca/dl） |
| `--verbose` | | 詳細輸出 |

## 實際測試結果

### fuji.png (正常方向)
- 原始圖像尺寸: 678 x 912
- 偵測文字區塊: 204 個
- 平均信心度: 87.33%
- 文字圖像: ✅ 成功生成

### fujid.png (倒轉 180°)
- 原始圖像尺寸: 678 x 912
- 偵測文字區塊: 184 個
- 平均信心度: 84.13%
- 自動方向校正: ✅ 已校正
- 文字圖像: ✅ 成功生成

## 應用場景

1. **文件數位化**
   - 將紙本文件轉換為純文字圖像
   - 保留原始排版位置

2. **識別效果對比**
   - 對比原圖和文字圖像
   - 檢查 OCR 識別準確度

3. **文字提取**
   - 從複雜背景中提取文字
   - 生成乾淨的文字版本

4. **資料處理管道**
   - 作為後續處理的中間結果
   - 可再次 OCR 或人工校對

## 故障排除

### 問題：中文字無法顯示

**解決方法：**
```bash
# 安裝中文字體（Ubuntu/Debian）
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# 安裝思源黑體
sudo apt-get install fonts-noto-cjk
```

### 問題：Pillow 未安裝

**解決方法：**
```bash
pip3 install Pillow
```

### 問題：字體太小/太大

修改 `ocr_parser.py` 中的字體大小：
```python
font = ImageFont.truetype(font_path, 20)  # 調整這個數字
```

## 更新日誌

### 2025-12-07
- ✨ 新增 `--text-image` 參數
- ✨ 新增 `create_text_image()` 方法
- ✅ 支援中文字體自動偵測
- ✅ 白底黑字的純文字圖像生成
- ✅ 保留原始文字位置
