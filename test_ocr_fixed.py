#!/usr/bin/env python3
"""測試 OCR 識別"""

import sys
sys.path.insert(0, '4_OCR_Recognition')
from ocr_parser import OCRParser

print("初始化 OCR...")
parser = OCRParser(lang='ch', use_gpu=False, verbose=False)

print("識別第一張圖片...")
result = parser.recognize('11_PDF_Pipeline/meta/images_rotated/page_001.png')

print(f'\n結果: success={result["success"]}, blocks={result.get("total_blocks", 0)}')

if result['success']:
    print("\n前 5 個文字塊:")
    for i, block in enumerate(result['text_blocks'][:5], 1):
        print(f'{i}. {block["text"]} (信心度: {block["confidence"]:.2f})')
else:
    print(f"錯誤: {result.get('error', '未知')}")
