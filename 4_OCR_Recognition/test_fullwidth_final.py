#!/usr/bin/env python3
"""
全形轉半形功能完整測試
"""

print('='*70)
print('🧪 全形轉半形功能測試')
print('='*70)
print()

# 測試 1: 轉換函數
print('📝 測試 1: 字符轉換函數')
print('-'*70)

from ocr_parser import OCRParser

test_cases = [
    ('全形數字', '１２３４５６７８９０', '1234567890'),
    ('全形英文大寫', 'ＡＢＣＤＥＦＧ', 'ABCDEFG'),
    ('全形英文小寫', 'ａｂｃｄｅｆｇ', 'abcdefg'),
    ('全形括號', '（）［］｛｝', '()[]{}'),
    ('全形標點', '：；，。！？', ':;,.!?'),
    ('全形符號', '＠＃＄％＾＆＊', '@#$%^&*'),
    ('全形加減號', '＋－＝', '+-='),
    ('全形斜線', '／＼', '/\\'),
    ('混合測試', '１２５０頁', '1250頁'),
    ('型號格式', 'Ｃ３２５／３２８', 'C325/328'),
    ('序號格式', 'ＮＣ７００３６７７', 'NC7003677'),
]

passed = 0
failed = 0

for description, original, expected in test_cases:
    result = OCRParser.fullwidth_to_halfwidth(original)
    if result == expected:
        print(f'✅ {description}')
        print(f'   "{original}" → "{result}"')
        passed += 1
    else:
        print(f'❌ {description}')
        print(f'   輸入: "{original}"')
        print(f'   輸出: "{result}"')
        print(f'   預期: "{expected}"')
        failed += 1
    print()

print(f'結果: {passed} 通過, {failed} 失敗')
print()

# 測試 2: 實際 OCR
print('='*70)
print('📝 測試 2: 實際 OCR 識別')
print('-'*70)
print()

import os
test_image = '../images/fuji.png'

if os.path.exists(test_image):
    print(f'測試圖片: {test_image}')
    print()
    
    # 啟用轉換
    print('正在執行 OCR（啟用全形轉半形）...')
    parser_on = OCRParser(verbose=False, convert_fullwidth=True)
    result_on = parser_on.recognize(test_image)
    
    # 停用轉換
    print('正在執行 OCR（停用全形轉半形）...')
    parser_off = OCRParser(verbose=False, convert_fullwidth=False)
    result_off = parser_off.recognize(test_image)
    
    print()
    print('比對結果：')
    print('-'*70)
    
    converted_blocks = []
    
    for i in range(len(result_on['text_blocks'])):
        text_on = result_on['text_blocks'][i]['text']
        text_off = result_off['text_blocks'][i]['text']
        
        if text_on != text_off:
            converted_blocks.append({
                'index': i,
                'original': text_off,
                'converted': text_on
            })
    
    if converted_blocks:
        print(f'找到 {len(converted_blocks)} 個包含全形字符的區塊：')
        print()
        for block in converted_blocks[:10]:  # 只顯示前 10 個
            print(f'區塊 {block["index"]}:')
            print(f'  原始: "{block["original"]}"')
            print(f'  轉換: "{block["converted"]}" ✓')
            print()
        
        if len(converted_blocks) > 10:
            print(f'... 還有 {len(converted_blocks) - 10} 個區塊被轉換')
    else:
        print('✓ 此圖片中沒有檢測到全形字符')
    
    print()
    print(f'總計: {result_on["total_blocks"]} 個文字區塊')
    print(f'轉換: {len(converted_blocks)} 個包含全形字符')
    
else:
    print(f'❌ 找不到測試圖片: {test_image}')

print()
print('='*70)
print('✅ 全形轉半形功能已整合到 OCR 識別器')
print('='*70)
print()
print('使用方式：')
print()
print('1. Python API:')
print('   parser = OCRParser(convert_fullwidth=True)  # 啟用（預設）')
print('   parser = OCRParser(convert_fullwidth=False) # 停用')
print()
print('2. 命令列:')
print('   python3 ocr_parser.py --image test.png      # 啟用（預設）')
print('   python3 ocr_parser.py --image test.png --no-convert-fullwidth  # 停用')
print()
