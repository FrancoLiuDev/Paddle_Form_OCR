#!/bin/bash
# 測試專案的獨立性

echo "================================"
echo "11_PDF_Pipeline 獨立性測試"
echo "================================"
echo ""

# 測試目錄
TEST_DIR="/tmp/pdf_pipeline_test_$$"

echo "📁 建立測試目錄: $TEST_DIR"
mkdir -p "$TEST_DIR"

# 複製專案（不包含外部依賴）
echo "📋 複製專案檔案..."
cp -r . "$TEST_DIR/"

# 進入測試目錄
cd "$TEST_DIR"

# 清理不需要的檔案
echo "🧹 清理測試環境..."
rm -rf meta/* output/* logs/*.log __pycache__ tools/__pycache__ tools/*/__pycache__

# 檢查依賴
echo ""
echo "🔍 檢查 Python 依賴..."
python3 -c "import fitz; print('✓ PyMuPDF 已安裝')" 2>/dev/null || echo "✗ PyMuPDF 未安裝 (pip install PyMuPDF)"
python3 -c "import PIL; print('✓ Pillow 已安裝')" 2>/dev/null || echo "✗ Pillow 未安裝 (pip install Pillow)"

# 檢查模組
echo ""
echo "🔍 檢查工具模組..."
python3 -c "from tools import PDFConverter; print('✓ PDFConverter 可匯入')" 2>/dev/null || echo "✗ PDFConverter 匯入失敗"

# 檢查配置
echo ""
echo "🔍 檢查配置檔..."
if [ -f "pipeline_config.json" ]; then
    echo "✓ pipeline_config.json 存在"
    python3 -c "import json; json.load(open('pipeline_config.json'))" && echo "✓ JSON 格式正確" || echo "✗ JSON 格式錯誤"
else
    echo "✗ pipeline_config.json 不存在"
fi

# 檢查執行腳本
echo ""
echo "🔍 檢查執行檔案..."
[ -f "pipeline.py" ] && echo "✓ pipeline.py 存在" || echo "✗ pipeline.py 不存在"
[ -x "run.sh" ] && echo "✓ run.sh 可執行" || echo "✗ run.sh 不可執行"

# 檢查目錄結構
echo ""
echo "🔍 檢查目錄結構..."
[ -d "tools" ] && echo "✓ tools/ 目錄存在" || echo "✗ tools/ 目錄不存在"
[ -d "input" ] && echo "✓ input/ 目錄存在" || echo "✗ input/ 目錄不存在"
[ -d "output" ] && echo "✓ output/ 目錄存在" || echo "✗ output/ 目錄不存在"
[ -d "logs" ] && echo "✓ logs/ 目錄存在" || echo "✗ logs/ 目錄不存在"
[ -d "meta" ] && echo "✓ meta/ 目錄存在" || echo "✗ meta/ 目錄不存在"

# 檢查文檔
echo ""
echo "🔍 檢查文檔..."
[ -f "README.md" ] && echo "✓ README.md 存在" || echo "✗ README.md 不存在"
[ -f "ARCHITECTURE.md" ] && echo "✓ ARCHITECTURE.md 存在" || echo "✗ ARCHITECTURE.md 不存在"
[ -f "PROJECT_STRUCTURE.md" ] && echo "✓ PROJECT_STRUCTURE.md 存在" || echo "✗ PROJECT_STRUCTURE.md 不存在"

# 如果有測試 PDF，執行測試
echo ""
if [ -f "input/013大安.pdf" ]; then
    echo "🚀 執行測試..."
    python3 pipeline.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 測試成功！專案可獨立運作"
    else
        echo ""
        echo "❌ 測試失敗"
    fi
else
    echo "ℹ️  沒有測試 PDF，跳過執行測試"
    echo "   （需要 input/013大安.pdf）"
fi

echo ""
echo "================================"
echo "測試完成"
echo "================================"
echo ""
echo "測試目錄: $TEST_DIR"
echo "保留測試環境以供檢查"
echo ""
echo "清理測試環境: rm -rf $TEST_DIR"
