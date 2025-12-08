#!/usr/bin/env python3
"""
智能欄位偵測工具 - 快速示範
使用多種 AI 增強策略自動推測欄位含義
"""

import json
from difflib import SequenceMatcher
import re

# 載入資料
with open('../4_OCR_Recognition/result/result_fuji.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
text_blocks = data['text_blocks']

print('='*70)
print('🤖 智能欄位偵測工具')
print('='*70)
print()

# ========== 工具 1: 模糊匹配 (Fuzzy Matching) ==========
print('🔧 工具 1: 模糊匹配 - 容錯字串比對')
print('-'*70)
print('即使有錯字、漏字也能找到相似的文字')
print()

target = "總印張數"
print(f'搜尋目標: "{target}"')
print('結果:')

for block in text_blocks[:30]:  # 只看前 30 個
    text = block['text']
    # 計算相似度
    similarity = SequenceMatcher(None, text, target).ratio()
    if similarity > 0.5:  # 相似度 > 50%
        print(f'  ✓ "{text}" (相似度: {similarity:.1%})')

print()

# ========== 工具 2: 語義關鍵字 (Semantic Keywords) ==========
print('🔧 工具 2: 語義關鍵字搜尋')
print('-'*70)
print('用多個相關關鍵字搜尋，提高匹配成功率')
print()

concept = "序號"
keywords = ['序號', '序号', '序列', '編號', '编号', 'serial', 'SN']
print(f'概念: {concept}')
print(f'關鍵字: {keywords}')
print('結果:')

for i, block in enumerate(text_blocks):
    text = block['text']
    for kw in keywords:
        if kw.lower() in text.lower():
            print(f'  ✓ 索引 {i}: "{text}" (匹配關鍵字: {kw})')
            # 顯示右邊的值
            if i+1 < len(text_blocks):
                print(f'    → 右邊的值: "{text_blocks[i+1]["text"]}"')
            break

print()

# ========== 工具 3: 正則表達式模式 (Pattern Recognition) ==========
print('🔧 工具 3: 模式識別 - 自動識別特定格式')
print('-'*70)
print('自動識別數字、日期、序號等常見格式')
print()

patterns = {
    '頁數格式': r'\d+\s*[頁页]',
    '序號格式': r'[A-Z]{2}\d{7,}',
    '型號格式': r'[A-Z]\d{3}',
    'IP位址': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
}

for pattern_name, pattern in patterns.items():
    print(f'{pattern_name}: {pattern}')
    found = []
    for block in text_blocks:
        matches = re.findall(pattern, block['text'])
        if matches:
            found.append(f'"{block["text"]}" → {matches}')
    if found:
        for f in found[:3]:  # 只顯示前 3 個
            print(f'  ✓ {f}')
    else:
        print(f'  (未找到)')
    print()

# ========== 工具 4: 位置關係分析 (Position Analysis) ==========
print('🔧 工具 4: 位置關係分析')
print('-'*70)
print('根據座標判斷欄位和值的對應關係')
print()

# 找出 "印张数" 的位置
for i, block in enumerate(text_blocks):
    if '印张数' in block['text']:
        field_bbox = block['bbox']
        field_x = field_bbox[1][0]
        field_y = (field_bbox[0][1] + field_bbox[2][1]) / 2
        
        print(f'欄位: "{block["text"]}"')
        print(f'位置: x={field_x:.0f}, y={field_y:.0f}')
        print(f'尋找右邊同一行的文字...')
        
        # 找右邊的值
        for j, next_block in enumerate(text_blocks[i+1:i+5], start=i+1):
            next_bbox = next_block['bbox']
            next_x = next_bbox[0][0]
            next_y = (next_bbox[0][1] + next_bbox[2][1]) / 2
            
            y_diff = abs(next_y - field_y)
            if next_x > field_x and y_diff < 20:  # 在右邊且同一行
                print(f'  ✓ 找到值: "{next_block["text"]}"')
                print(f'    位置: x={next_x:.0f}, y={next_y:.0f}')
                print(f'    距離: x差={next_x-field_x:.0f}px, y差={y_diff:.0f}px')
                break
        break

print()

# ========== 總結 ==========
print('='*70)
print('💡 這些工具可以幫助你：')
print('='*70)
print('1. 🔤 模糊匹配: 處理 OCR 錯字、漏字')
print('   範例: "總印張數" 可以找到 "印张数"')
print()
print('2. 🔍 語義搜尋: 用多個關鍵字提高命中率')
print('   範例: ["序號","序号","序赋"] 增加容錯性')
print()
print('3. 🎯 模式識別: 自動識別數字、日期、序號格式')
print('   範例: 自動找出所有 "1250頁" 這種格式')
print()
print('4. 📐 位置分析: 根據座標找出欄位與值的對應')
print('   範例: "印张数" 右邊 → "1250页"')
print('='*70)
print()
print('💾 完整工具類別請參考: smart_field_detector.py')
