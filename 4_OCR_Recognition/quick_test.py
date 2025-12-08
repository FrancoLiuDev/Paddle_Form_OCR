#!/usr/bin/env python3
from ocr_parser import OCRParser

print('='*70)
print('全形轉半形功能測試')
print('='*70)
print()

test_cases = [
    ('１２３４５', '12345'),
    ('ＡＢＣ', 'ABC'),
    ('（）', '()'),
    ('１２５０頁', '1250頁'),
]

for original, expected in test_cases:
    result = OCRParser.fullwidth_to_halfwidth(original)
    status = '✅' if result == expected else '❌'
    print(f'{status} "{original}" → "{result}"')

print()
print('✨ 功能已加入!')
