#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速範例：從 OCR 結果提取「1250頁」
"""

import json
import re


def quick_extract_pages(json_path: str) -> dict:
    """
    快速提取頁數資訊
    
    Args:
        json_path: OCR 結果 JSON 檔案路徑
    
    Returns:
        包含所有頁數資訊的字典
    """
    # 讀取 OCR 結果
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {
        'all_pages': [],      # 所有找到的頁數
        'max_pages': None,    # 最大頁數（通常是總頁數）
        'details': []         # 詳細資訊
    }
    
    # 遍歷所有文字區塊
    for block in data['text_blocks']:
        text = block['text']
        
        # 檢查是否包含「頁」或「页」
        if '頁' in text or '页' in text:
            # 提取數字
            numbers = re.findall(r'\d+', text)
            if numbers:
                # 取最大的數字（如果有多個）
                page_num = int(max(numbers, key=lambda x: int(x)))
                
                results['all_pages'].append(page_num)
                results['details'].append({
                    'text': text,
                    'number': page_num,
                    'confidence': block['confidence']
                })
    
    # 找出最大頁數
    if results['all_pages']:
        results['max_pages'] = max(results['all_pages'])
    
    return results


def main():
    """主程式"""
    print("=" * 60)
    print("快速範例：提取頁數資訊")
    print("=" * 60)
    
    # 提取頁數
    result = quick_extract_pages('result/result_fuji.json')
    
    print(f"\n找到 {len(result['all_pages'])} 個頁數:")
    for detail in result['details']:
        print(f"  • {detail['text']:15s} → {detail['number']:4d} 頁 "
              f"(信心度: {detail['confidence']*100:.1f}%)")
    
    print(f"\n📊 總頁數: {result['max_pages']} 頁")
    
    # 單獨提取最大頁數（通常是總頁數）
    print("\n" + "=" * 60)
    print("如果只需要最大頁數（總頁數）：")
    print("=" * 60)
    print(f">>> {result['max_pages']} 頁")


if __name__ == '__main__':
    main()
