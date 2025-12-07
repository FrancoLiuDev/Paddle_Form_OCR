# 快速開始：文字圖像生成 ✨

## 一行命令生成純文字圖像

```bash
# 基本用法
python3 ocr_parser.py --image INPUT.png --text-image OUTPUT.jpg --verbose
```

## 實際範例

```bash
# 範例 1: fuji.png
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --text-image result/fuji_text.jpg \
    --verbose

# 範例 2: 倒轉的圖片（會自動校正）
python3 ocr_parser.py \
    --image ../images/fujid.png \
    --text-image result/fujid_text.jpg \
    --verbose
```

## 輸出結果

生成的 `*_text.jpg` 是：
- ✅ 白色背景
- ✅ 黑色文字
- ✅ 保留原始位置
- ✅ 支援中文顯示

## 完整功能

```bash
# 同時生成 JSON、可視化和文字圖像
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --output result/output.json \
    --visualize result/output_boxes.jpg \
    --text-image result/output_text.jpg \
    --verbose
```

## 快速測試

```bash
# 執行示範腳本
./demo_text_image.sh
```

詳細說明請參考 `README_TEXT_IMAGE.md`
