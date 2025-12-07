#!/bin/bash
# OCR 文字圖像生成 - 快速範例

echo "========================================"
echo "OCR 文字圖像生成測試"
echo "========================================"
echo ""

# 測試 1: 生成 fuji.png 的文字圖像
echo "1. 測試 fuji.png (正常方向)"
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --text-image result/demo_fuji_text.jpg \
    --verbose

echo ""
echo "========================================"
echo ""

# 測試 2: 生成 fujid.png 的文字圖像（倒轉的圖片）
echo "2. 測試 fujid.png (倒轉 180°，會自動校正)"
python3 ocr_parser.py \
    --image ../images/fujid.png \
    --text-image result/demo_fujid_text.jpg \
    --verbose

echo ""
echo "========================================"
echo ""

# 測試 3: 完整輸出（JSON + 可視化 + 文字圖像）
echo "3. 完整測試：生成所有輸出檔案"
python3 ocr_parser.py \
    --image ../images/fuji.png \
    --output result/demo_complete.json \
    --visualize result/demo_complete_visual.jpg \
    --text-image result/demo_complete_text.jpg \
    --verbose

echo ""
echo "========================================"
echo "✅ 測試完成！"
echo "========================================"
echo ""
echo "生成的檔案："
ls -lh result/demo_* 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "檔案說明："
echo "  • *_text.jpg     - 白底黑字的純文字圖像 ✨"
echo "  • *_visual.jpg   - 原圖 + 綠色框標註"
echo "  • *.json         - 完整識別結果（JSON 格式）"
echo ""
