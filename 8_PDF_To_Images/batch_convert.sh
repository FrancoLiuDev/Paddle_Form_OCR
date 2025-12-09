#!/bin/bash
# 批次轉換多個 PDF 檔案

echo "🚀 批次 PDF 轉圖片工具"
echo "================================"
echo ""

# 檢查 input 目錄
if [ ! -d "input" ]; then
    echo "❌ 找不到 input 目錄"
    exit 1
fi

# 計算 PDF 數量
pdf_count=$(find input -name "*.pdf" | wc -l)

if [ $pdf_count -eq 0 ]; then
    echo "❌ input 目錄中沒有 PDF 檔案"
    exit 1
fi

echo "📁 找到 $pdf_count 個 PDF 檔案"
echo ""

# 詢問設定
echo "請選擇品質設定:"
echo "  1) 快速 (150 DPI)"
echo "  2) 標準 (300 DPI) [預設]"
echo "  3) 高品質 (600 DPI)"
read -p "請選擇 [1-3]: " choice

case $choice in
    1) DPI=150 ;;
    3) DPI=600 ;;
    *) DPI=300 ;;
esac

echo ""
echo "請選擇格式:"
echo "  1) PNG (無損) [預設]"
echo "  2) JPG (壓縮)"
read -p "請選擇 [1-2]: " format_choice

case $format_choice in
    2) FORMAT="JPG" ;;
    *) FORMAT="PNG" ;;
esac

echo ""
echo "⚙️  設定: $DPI DPI, $FORMAT 格式"
echo "================================"
echo ""

# 處理每個 PDF
count=0
for pdf in input/*.pdf; do
    if [ -f "$pdf" ]; then
        count=$((count + 1))
        echo "[$count/$pdf_count] 處理: $(basename "$pdf")"
        python3 pdf_to_images.py "$pdf" --dpi $DPI --format $FORMAT
        echo ""
    fi
done

echo "✨ 全部完成！"
echo "輸出目錄: output/"
