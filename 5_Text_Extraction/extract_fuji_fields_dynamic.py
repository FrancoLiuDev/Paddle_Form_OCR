#!/usr/bin/env python3
"""
動態提取 fuji.png 中的印表機資訊欄位
使用模糊匹配自動判斷，不需要預先定義候選名單
"""
import json
import re
from difflib import SequenceMatcher

def fuzzy_match(text: str, target: str, threshold: float = 0.6) -> float:
    """
    計算兩個字串的相似度（改進版）
    
    支援部分匹配：如果 text 包含 target 的主要部分，也算匹配
    
    Args:
        text: 待比對字串
        target: 目標字串
        threshold: 相似度門檻
    
    Returns:
        相似度分數 (0-1)
    """
    # 方法 1: 完整字串相似度
    full_similarity = SequenceMatcher(None, text, target).ratio()
    
    # 方法 2: 去掉常見前綴後比對
    # 例如："總印張數" → "印張數" or "印张数"
    prefixes = ['總', '全', '总', '全部', '所有']
    
    max_similarity = full_similarity
    
    for prefix in prefixes:
        if target.startswith(prefix):
            # 去掉前綴後的目標
            target_without_prefix = target[len(prefix):]
            # 計算相似度
            sim = SequenceMatcher(None, text, target_without_prefix).ratio()
            max_similarity = max(max_similarity, sim)
    
    # 方法 3: 繁簡轉換後比對
    # 張→张, 數→数, 機→机
    conversions = [
        ('張', '张'), ('數', '数'), ('機', '机'),
        ('稱', '称'), ('號', '号'), ('與', '与')
    ]
    
    for trad, simp in conversions:
        if trad in target:
            target_simp = target.replace(trad, simp)
            sim = SequenceMatcher(None, text, target_simp).ratio()
            max_similarity = max(max_similarity, sim)
            
            # 同時嘗試去掉前綴
            for prefix in prefixes:
                if target_simp.startswith(prefix):
                    target_clean = target_simp[len(prefix):]
                    sim = SequenceMatcher(None, text, target_clean).ratio()
                    max_similarity = max(max_similarity, sim)
    
    # 方法 4: 包含檢查（關鍵詞匹配）
    # 如果 text 包含在 target 中，或 target 的一部分在 text 中
    if text in target or target in text:
        # 根據長度比例計算相似度
        max_similarity = max(max_similarity, 
                            min(len(text), len(target)) / max(len(text), len(target)))
    
    return max_similarity

def find_field_by_fuzzy_match(text_blocks, field_name, threshold=0.5):
    """
    使用模糊匹配動態尋找欄位
    
    Args:
        text_blocks: OCR文字區塊列表
        field_name: 要尋找的欄位名稱
        threshold: 相似度門檻
    
    Returns:
        匹配到的區塊索引和相似度
    """
    best_match = None
    best_similarity = 0
    
    for i, block in enumerate(text_blocks):
        text = block['text'].strip()
        
        # 計算相似度
        similarity = fuzzy_match(text, field_name, threshold)
        
        # 如果相似度超過門檻且更高
        if similarity >= threshold and similarity > best_similarity:
            best_similarity = similarity
            best_match = {
                'index': i,
                'text': text,
                'similarity': similarity,
                'confidence': block['confidence']
            }
    
    return best_match

def find_value_by_position(text_blocks, field_index, search_range=5):
    """
    根據欄位位置找右邊的值
    
    Args:
        text_blocks: OCR文字區塊列表
        field_index: 欄位的索引
        search_range: 搜尋範圍
    
    Returns:
        找到的值資訊
    """
    if field_index >= len(text_blocks):
        return None
    
    field = text_blocks[field_index]
    bbox = field['bbox']
    field_x = bbox[1][0]  # 欄位右邊的 x 座標
    field_y = (bbox[0][1] + bbox[2][1]) / 2  # 欄位 y 中心
    
    candidates = []
    
    for i in range(field_index + 1, min(field_index + search_range, len(text_blocks))):
        next_block = text_blocks[i]
        next_bbox = next_block['bbox']
        next_x = next_bbox[0][0]
        next_y = (next_bbox[0][1] + next_bbox[2][1]) / 2
        
        # 檢查是否在同一行且在右邊
        y_diff = abs(next_y - field_y)
        if next_x > field_x and y_diff < 20:
            candidates.append({
                'value': next_block['text'].strip(),
                'confidence': next_block['confidence'],
                'distance': next_x - field_x,
                'y_diff': y_diff
            })
    
    # 選擇最接近的候選值
    if candidates:
        candidates.sort(key=lambda x: (x['y_diff'], x['distance']))
        return candidates[0]
    
    return None

def extract_field_dynamic(text_blocks, field_name, threshold=0.5):
    """
    動態提取欄位值
    
    Args:
        text_blocks: OCR文字區塊列表
        field_name: 欄位名稱
        threshold: 相似度門檻
    
    Returns:
        提取結果
    """
    # 1. 使用模糊匹配找欄位
    field_match = find_field_by_fuzzy_match(text_blocks, field_name, threshold)
    
    if not field_match:
        return None
    
    # 2. 根據位置找對應的值
    value_info = find_value_by_position(text_blocks, field_match['index'])
    
    if not value_info:
        return None
    
    return {
        'field_text': field_match['text'],
        'field_similarity': field_match['similarity'],
        'field_confidence': field_match['confidence'],
        'value': value_info['value'],
        'value_confidence': value_info['confidence']
    }

def semantic_field_detection(text_blocks):
    """
    使用語義分析自動偵測可能的欄位
    
    Returns:
        檢測到的欄位列表
    """
    detected_fields = []
    
    # 常見欄位的語義特徵
    semantic_patterns = {
        '印表機相關': ['印表', '打印', '列印', '機型', '型號'],
        '數量相關': ['張數', '次數', '頁數', '印', '數'],
        '識別碼相關': ['序號', '編號', 'SN', 'Serial', '序列'],
        '日期時間': ['日期', '時間', '年', '月', '日'],
        '網路相關': ['IP', '位址', 'DHCP', '網路']
    }
    
    for i, block in enumerate(text_blocks):
        text = block['text'].strip()
        
        # 跳過太短的文字
        if len(text) < 2:
            continue
        
        # 檢查是否包含欄位特徵
        for category, keywords in semantic_patterns.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    detected_fields.append({
                        'index': i,
                        'text': text,
                        'category': category,
                        'keyword': keyword,
                        'confidence': block['confidence']
                    })
                    break
    
    return detected_fields

def main():
    # 讀取 OCR 結果
    json_file = '../4_OCR_Recognition/result/result_fuji_test.json'
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text_blocks = data.get('text_blocks', [])
    
    print('\n' + '='*70)
    print('🤖 動態欄位提取 - 使用模糊匹配和語義分析')
    print('='*70 + '\n')
    
    # 要提取的欄位（只需要目標名稱，不需要候選列表）
    target_fields = {
        '印表機名稱': 0.5,  # 欄位名稱: 相似度門檻
        '總印張數': 0.4,
        '彩色印張數': 0.5,
        '黑白印張數': 0.5,
        '序號': 0.4
    }
    
    results = {}
    
    print('📋 方法 1: 模糊匹配提取')
    print('-'*70)
    
    # 動態提取每個欄位
    for field_name, threshold in target_fields.items():
        result = extract_field_dynamic(text_blocks, field_name, threshold)
        
        if result:
            results[field_name] = result
            print(f'✅ 【{field_name}】')
            print(f'   欄位識別: "{result["field_text"]}" (相似度: {result["field_similarity"]:.1%})')
            print(f'   值: "{result["value"]}" (信心度: {result["value_confidence"]*100:.1f}%)')
            print()
        else:
            print(f'❌ 【{field_name}】未找到 (門檻: {threshold})')
            print()
    
    # 語義分析：自動偵測所有可能的欄位
    print('\n' + '='*70)
    print('📋 方法 2: 語義分析 - 自動偵測欄位')
    print('-'*70)
    
    detected = semantic_field_detection(text_blocks)
    
    # 按類別分組
    by_category = {}
    for field in detected:
        category = field['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(field)
    
    for category, fields in by_category.items():
        print(f'\n🏷️  {category}:')
        for field in fields[:3]:  # 只顯示前 3 個
            print(f'   • "{field["text"]}" (匹配關鍵字: {field["keyword"]})')
    
    print('\n' + '='*70)
    print(f'✨ 模糊匹配成功提取 {len(results)}/{len(target_fields)} 個欄位')
    print(f'✨ 語義分析偵測到 {len(detected)} 個可能的欄位')
    print('='*70 + '\n')
    
    # 儲存結果
    output = {
        'extraction_method': 'dynamic_fuzzy_matching',
        'extracted_fields': {
            field: {
                'value': info['value'],
                'value_confidence': f'{info["value_confidence"]*100:.1f}%',
                'field_text': info['field_text'],
                'field_similarity': f'{info["field_similarity"]:.1%}'
            }
            for field, info in results.items()
        },
        'detected_fields': [
            {
                'text': f['text'],
                'category': f['category']
            }
            for f in detected
        ],
        'total_extracted': len(results),
        'total_detected': len(detected)
    }
    
    output_file = 'result/fuji_printer_info_dynamic.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f'💾 結果已儲存至: {output_file}')

if __name__ == '__main__':
    main()
