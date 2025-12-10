#!/bin/bash
# Pipeline 執行腳本

cd "$(dirname "$0")"

echo "================================"
echo "PDF Processing Pipeline"
echo "================================"
echo ""

# 檢查 input 目錄
if [ ! -d "input" ]; then
    echo "✗ 錯誤: input/ 目錄不存在"
    exit 1
fi

# 檢查是否有 PDF 檔案
pdf_count=$(ls -1 input/*.pdf 2>/dev/null | wc -l)

if [ $pdf_count -eq 0 ]; then
    echo "✗ 錯誤: input/ 目錄中沒有 PDF 檔案"
    echo "請將 PDF 檔案放入 input/ 目錄"
    exit 1
fi

if [ $pdf_count -gt 1 ]; then
    echo "✗ 錯誤: input/ 目錄中有多個 PDF 檔案 ($pdf_count 個)"
    echo "請確保只有一個 PDF 檔案"
    exit 1
fi

pdf_file=$(ls input/*.pdf)
echo "✓ 找到輸入檔案: $pdf_file"
echo ""

# 執行 Pipeline
python3 pipeline.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ Pipeline 執行成功"
    echo "================================"
else
    echo ""
    echo "================================"
    echo "✗ Pipeline 執行失敗"
    echo "================================"
fi

exit $exit_code
