#!/usr/bin/env python3
"""
專門提取 fuji.png 中的印表機資訊欄位
"""
import json
import sys

def extract_field_value(text_blocks, field_keywords, search_range=5):
    """
    搜尋欄位名稱並提取右邊的值
    
    Args:
        text_blocks: OCR文字區塊列表
        field_keywords: 欄位關鍵字列表
        search_range: 搜尋右邊多少個區塊
    
    Returns:
        提取到的值資訊，若無則返回 None
    """
    for i, block in enumerate(text_blocks):
        text = block['text'].strip()
        
        # 檢查是否包含任何關鍵字
        for keyword in field_keywords:
            if keyword in text:
                # 找到欄位，查找右邊的值
                # 通常值在同一行右側或下一個區塊
                bbox = block['bbox']
                field_x = bbox[1][0]  # 欄位右邊的 x 座標
                field_y = (bbox[0][1] + bbox[2][1]) / 2  # 欄位 y 中心
                
                # 搜尋右邊相近位置的文字區塊
                candidates = []
                for j in range(i+1, min(i+search_range, len(text_blocks))):
                    next_block = text_blocks[j]
                    next_bbox = next_block['bbox']
                    next_x = next_bbox[0][0]  # 下一個區塊左邊的 x 座標
                    next_y = (next_bbox[0][1] + next_bbox[2][1]) / 2
                    
                    # 檢查是否在同一行（y 座標接近）且在右邊（x 座標更大）
                    y_diff = abs(next_y - field_y)
                    if next_x > field_x and y_diff < 20:  # 同一行，容許 20px 誤差
                        candidates.append({
                            'value': next_block['text'].strip(),
                            'confidence': next_block['confidence'],
                            'distance': next_x - field_x,
                            'y_diff': y_diff
                        })
                
                # 選擇最接近的候選值（x距離最小）
                if candidates:
                    candidates.sort(key=lambda x: (x['y_diff'], x['distance']))
                    best = candidates[0]
                    return {
                        'field_text': text,
                        'value': best['value'],
                        'confidence': best['confidence'],
                        'matched_keyword': keyword
                    }
    
    return None

def main():
    # 讀取 OCR 結果
    json_file = '../4_OCR_Recognition/result/result_fuji_test.json'
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    text_blocks = data.get('text_blocks', [])
    
    # 定義要提取的欄位
    fields = {
        '印表機名稱': ['印表機名稠', '印表機名稱', '印表名稠', '印表名称'],
        '總印張數': ['總印張數', '总印张数', '印张数'],
        '彩色印張數': ['彩色印張數', '彩色印张数', '彩色印'],
        '黑白印張數': ['黑白印張數', '黑白印张数', '黑白印次', '黑白印'],
        '序號': ['序號', '序号', '序赋', '序列号', '编号']
    }
    
    print('\n' + '='*70)
    print('📊 fuji.png 印表機資訊提取結果')
    print('='*70 + '\n')
    
    results = {}
    
    # 提取每個欄位
    for field_name, keywords in fields.items():
        result = extract_field_value(text_blocks, keywords)
        
        if result:
            results[field_name] = result
            print(f'✅ 【{field_name}】')
            print(f'   欄位識別: {result["field_text"]}')
            print(f'   值: {result["value"]}')
            print(f'   信心度: {result["confidence"]*100:.1f}%')
            print()
        else:
            print(f'❌ 【{field_name}】未找到')
            print(f'   搜尋關鍵字: {", ".join(keywords)}')
            print()
    
    print('='*70)
    print(f'✨ 成功提取 {len(results)}/{len(fields)} 個欄位')
    print('='*70 + '\n')
    
    # 儲存結果
    output = {
        'extracted_fields': {
            field: {
                'value': info['value'],
                'confidence': f'{info["confidence"]*100:.1f}%',
                'field_text': info['field_text']
            }
            for field, info in results.items()
        },
        'total_fields': len(fields),
        'extracted_count': len(results)
    }
    
    output_file = 'result/fuji_printer_info.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f'💾 結果已儲存至: {output_file}')

if __name__ == '__main__':
    main()
