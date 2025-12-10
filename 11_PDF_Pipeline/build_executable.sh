#!/bin/bash
# 打包 11_PDF_Pipeline 為可執行程式

echo "================================"
echo "11_PDF_Pipeline 打包工具"
echo "================================"
echo ""

# 檢查 PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 安裝 PyInstaller..."
    pip3 install pyinstaller
fi

# 清理舊的打包結果
echo "🧹 清理舊的打包檔案..."
rm -rf build/ dist/ *.spec

# 打包
echo ""
echo "📦 開始打包..."
echo ""

pyinstaller --onefile \
    --name pdf_pipeline \
    --add-data "pipeline_config.json:." \
    --add-data "tools:tools" \
    --hidden-import=tools \
    --hidden-import=tools.pdf_converter \
    --clean \
    pipeline.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ 打包成功！"
    echo "================================"
    echo ""
    echo "執行檔位置: dist/pdf_pipeline"
    echo ""
    echo "使用方式："
    echo "  1. 將 dist/pdf_pipeline 複製到目標目錄"
    echo "  2. 在該目錄建立 input/ 目錄並放入 PDF"
    echo "  3. 執行: ./pdf_pipeline"
    echo ""
else
    echo ""
    echo "================================"
    echo "✗ 打包失敗"
    echo "================================"
    exit 1
fi
