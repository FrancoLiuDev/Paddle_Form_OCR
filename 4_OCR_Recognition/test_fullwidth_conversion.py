#!/usr/bin/env python3
"""
測試全形轉半形功能
"""

import sys
sys.path.insert(0, '/home/franco/Documents/Project/Paddle_Form_OCR/4_OCR_Recognition')
from ocr_parser import OCRParser

print('='*70)
print('🔧 全形轉半形功能測試')
print('='*70)
print()

# 測試轉換函數
print('📝 測試 1: 轉換函數單元測試')
print('-'*70)

test_cases = [
    ("１２３４５６７８９０", "1234567890"),
    ("ＡＢＣＤＥabcde", "ABCDEabcde"),
    ("（）［］｛｝", "()[]{}"),
    ("：；，。！？", ":;,.!?"),
    ("＠＃＄％＾＆", "@#$%^&"),
    ("全形空格　測試", "全形空格 測試"),
    ("１２５０頁", "1250頁"),
    ("Ｃ３２５／３２８", "C325/328"),
    ("ＮＣ７００３６７７", "NC7003677"),
]

for original, expected in test_cases:
    result = OCRParser.fullwidth_to_halfwidth(original)
    status = "✅" if result == expected else "❌"
    print(f'{status} "{original}" → "{result}"')
    if result != expected:
        print(f'   預期: "{expected}"')

print()
print('='*70)
print('✨ 功能特點：')
print('  • 全形數字 → 半形數字 (１２３ → 123)')
print('  • 全形英文 → 半形英文 (ＡＢＣ → ABC)')
print('  • 全形符號 → 半形符號 (：；， → :;,)')
print('  • 全形空格 → 半形空格')
print('  • 中文字符保持不變')
print('='*70)
print()

print('📝 測試 2: OCR 實際識別測試')
print('-'*70)
print('如果 OCR 識別出全形字符，將自動轉換為半形')
print()

# 測試 OCR（如果有測試圖片）
import os
test_image = '/home/franco/Documents/Project/Paddle_Form_OCR/images/fuji.png'

if os.path.exists(test_image):
    print(f'正在測試圖片: {test_image}')
    print()
    
    # 使用轉換功能
    parser_with_convert = OCRParser(verbose=False, convert_fullwidth=True)
    result_with = parser_with_convert.recognize(test_image)
    
    # 不使用轉換功能
    parser_without_convert = OCRParser(verbose=False, convert_fullwidth=False)
    result_without = parser_without_convert.recognize(test_image)
    
    print('前 10 個文字區塊比對：')
    print()
    
    conversion_count = 0
    for i in range(min(10, len(result_with['text_blocks']))):
        text_with = result_with['text_blocks'][i]['text']
        text_without = result_without['text_blocks'][i]['text']
        
        if text_with != text_without:
            conversion_count += 1
            print(f'區塊 {i+1}:')
            print(f'  原始: "{text_without}"')
            print(f'  轉換: "{text_with}" ✓')
            print()
    
    if conversion_count == 0:
        print('✓ 此圖片中沒有全形字符，或已經是半形')
    else:
        print(f'✓ 共轉換了 {conversion_count} 個文字區塊')
    
    # 檢查整體統計
    total_converted = sum(1 for block in result_with['text_blocks'] 
                         if 'original_text' in block)
    
    print()
    print(f'總計: {result_with["total_blocks"]} 個文字區塊')
    print(f'轉換: {total_converted} 個包含全形字符')
    
else:
    print(f'⚠️ 找不到測試圖片: {test_image}')

print()
print('='*70)
print('💡 使用方式：')
print('='*70)
print()
print('# 啟用全形轉半形（預設）')
print('parser = OCRParser(convert_fullwidth=True)')
print()
print('# 停用全形轉半形')
print('parser = OCRParser(convert_fullwidth=False)')
print()
print('# 在命令列中使用')
print('python3 ocr_parser.py --image test.png --convert-fullwidth')
print()
