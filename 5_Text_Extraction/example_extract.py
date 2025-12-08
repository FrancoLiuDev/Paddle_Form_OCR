#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 使用範例
展示如何在程式中使用 TextExtractor
"""

from text_extractor import TextExtractor


def example_basic_extraction():
    """範例 1: 基礎提取"""
    print("=" * 70)
    print("範例 1: 基礎文字提取")
    print("=" * 70)
    
    # 初始化提取器
    extractor = TextExtractor(
        '../4_OCR_Recognition/result/result_fuji.json',
        verbose=True
    )
    
    # 1. 提取頁數
    print("\n【提取頁數】")
    pages = extractor.extract_pages()
    print(f"總頁數: {pages['max_pages']}")
    print(f"詳細資訊: {len(pages['details'])} 個區塊")
    
    # 2. 關鍵字搜尋
    print("\n【關鍵字搜尋】")
    results = extractor.extract_by_keyword('系統')
    print(f"找到 {len(results)} 個包含「系統」的文字")
    for r in results[:3]:  # 只顯示前3個
        print(f"  • {r['text']}")


def example_regex_extraction():
    """範例 2: 正則表達式提取"""
    print("\n" + "=" * 70)
    print("範例 2: 正則表達式提取")
    print("=" * 70)
    
    extractor = TextExtractor('../4_OCR_Recognition/result/result_fuji.json')
    
    # 1. 提取所有數字+頁的格式
    print("\n【數字+頁】")
    results = extractor.extract_by_regex(r'\d+\s*[頁页]')
    for r in results:
        print(f"  • {r['text']} → 匹配: {r['matches']}")
    
    # 2. 提取日期
    print("\n【日期格式】")
    dates = extractor.extract_dates()
    for d in dates[:3]:
        print(f"  • {d['text']}")


def example_advanced_extraction():
    """範例 3: 高級提取（多條件組合）"""
    print("\n" + "=" * 70)
    print("範例 3: 多條件組合提取")
    print("=" * 70)
    
    extractor = TextExtractor('../4_OCR_Recognition/result/result_fuji.json')
    
    # 組合條件：關鍵字 + 正則 + 信心度
    print("\n【條件】關鍵字=「页」+ 4位數字 + 信心度>90%")
    results = extractor.extract_with_conditions(
        keyword='页',
        pattern=r'\d{4}',
        min_confidence=0.9
    )
    
    print(f"找到 {len(results)} 個符合的結果:")
    for r in results:
        print(f"  • {r['text']} (信心度: {r['confidence']*100:.1f}%)")


def example_summary():
    """範例 4: 取得摘要"""
    print("\n" + "=" * 70)
    print("範例 4: OCR 結果摘要")
    print("=" * 70)
    
    extractor = TextExtractor('../4_OCR_Recognition/result/result_fuji.json')
    
    summary = extractor.get_summary()
    
    print(f"\n總文字區塊數: {summary['total_blocks']}")
    print(f"平均信心度: {summary['avg_confidence']*100:.2f}%")
    print(f"信心度範圍: {summary['min_confidence']*100:.2f}% - {summary['max_confidence']*100:.2f}%")
    print(f"高信心度區塊 (>90%): {summary['high_confidence_blocks']}")
    print(f"旋轉角度: {summary['rotation_angle']}°")


def example_custom_pattern():
    """範例 5: 自訂提取模式"""
    print("\n" + "=" * 70)
    print("範例 5: 自訂提取模式")
    print("=" * 70)
    
    extractor = TextExtractor('../4_OCR_Recognition/result/result_fuji.json')
    
    # 自訂模式：提取所有包含數字的文字
    print("\n【所有包含數字的文字】")
    results = extractor.extract_by_regex(r'\d+')
    print(f"找到 {len(results)} 個包含數字的文字區塊")
    
    # 統計數字
    all_numbers = []
    for r in results:
        numbers = extractor.extract_numbers(r['text'])
        all_numbers.extend(numbers)
    
    if all_numbers:
        print(f"\n數字統計:")
        print(f"  總共提取: {len(all_numbers)} 個數字")
        print(f"  最大值: {max(all_numbers)}")
        print(f"  最小值: {min(all_numbers)}")
        print(f"  總和: {sum(all_numbers)}")


def example_export_data():
    """範例 6: 匯出提取的資料"""
    print("\n" + "=" * 70)
    print("範例 6: 匯出提取資料")
    print("=" * 70)
    
    import json
    
    extractor = TextExtractor('../4_OCR_Recognition/result/result_fuji.json')
    
    # 提取多種資料
    export_data = {
        'pages': extractor.extract_pages(),
        'dates': extractor.extract_dates(),
        'summary': extractor.get_summary(),
    }
    
    # 儲存為 JSON
    output_file = 'examples/extracted_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 資料已匯出至: {output_file}")


def main():
    """執行所有範例"""
    print("\n" + "=" * 70)
    print("Text Extractor Python 使用範例")
    print("=" * 70)
    
    try:
        example_basic_extraction()
        example_regex_extraction()
        example_advanced_extraction()
        example_summary()
        example_custom_pattern()
        
        # 創建 examples 目錄
        import os
        os.makedirs('examples', exist_ok=True)
        example_export_data()
        
        print("\n" + "=" * 70)
        print("✅ 所有範例執行完成")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n❌ 錯誤: {e}")
        print("\n請確保:")
        print("  1. 已在 4_OCR_Recognition 中生成 result_fuji.json")
        print("  2. 執行命令: cd 4_OCR_Recognition && python3 ocr_parser.py --image ../images/fuji.png --output result/result_fuji.json")


if __name__ == '__main__':
    main()
