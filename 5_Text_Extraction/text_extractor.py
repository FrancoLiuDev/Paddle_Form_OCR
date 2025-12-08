#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字提取專用程式
從 PaddleOCR 識別結果中提取特定的文字和數據
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class TextExtractor:
    """文字提取器 - 從 OCR 結果中提取特定格式的文字和數據"""
    
    def __init__(self, json_path: str, verbose: bool = False):
        """
        初始化提取器
        
        Args:
            json_path: OCR 結果 JSON 檔案路徑
            verbose: 是否顯示詳細資訊
        """
        self.verbose = verbose
        self.json_path = json_path
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.text_blocks = self.data.get('text_blocks', [])
            
            if self.verbose:
                print(f"✓ 已載入 OCR 結果: {len(self.text_blocks)} 個文字區塊")
        except FileNotFoundError:
            print(f"❌ 錯誤: 找不到檔案 {json_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ 錯誤: 無效的 JSON 格式")
            sys.exit(1)
    
    # ==================== 基礎提取方法 ====================
    
    def extract_by_keyword(self, keyword: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        通過關鍵字提取文字
        
        Args:
            keyword: 關鍵字
            case_sensitive: 是否區分大小寫
        
        Returns:
            包含關鍵字的文字區塊列表
        """
        results = []
        
        for block in self.text_blocks:
            text = block['text']
            
            if case_sensitive:
                match = keyword in text
            else:
                match = keyword.lower() in text.lower()
            
            if match:
                results.append({
                    'text': text,
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        
        return results
    
    def extract_by_regex(self, pattern: str, extract_groups: bool = False) -> List[Dict[str, Any]]:
        """
        使用正則表達式提取文字
        
        Args:
            pattern: 正則表達式模式
            extract_groups: 是否提取捕獲組
        
        Returns:
            匹配的文字區塊列表
        """
        results = []
        regex = re.compile(pattern)
        
        for block in self.text_blocks:
            text = block['text']
            
            if extract_groups:
                match = regex.search(text)
                if match:
                    results.append({
                        'text': text,
                        'matches': match.groups(),
                        'confidence': block['confidence'],
                        'bbox': block['bbox']
                    })
            else:
                matches = regex.findall(text)
                if matches:
                    results.append({
                        'text': text,
                        'matches': matches,
                        'confidence': block['confidence'],
                        'bbox': block['bbox']
                    })
        
        return results
    
    def extract_numbers(self, text: str) -> List[int]:
        """
        從文字中提取所有數字
        
        Args:
            text: 輸入文字
        
        Returns:
            數字列表
        """
        numbers = re.findall(r'\d+', text)
        return [int(n) for n in numbers]
    
    # ==================== 專用提取方法 ====================
    
    def extract_pages(self, keywords: List[str] = ['頁', '页', 'page']) -> Dict[str, Any]:
        """
        提取頁數資訊
        
        Args:
            keywords: 頁數關鍵字列表
        
        Returns:
            包含頁數資訊的字典
        """
        results = {
            'all_pages': [],
            'max_pages': None,
            'details': []
        }
        
        for block in self.text_blocks:
            text = block['text']
            
            # 檢查是否包含關鍵字
            if any(kw in text for kw in keywords):
                numbers = self.extract_numbers(text)
                
                if numbers:
                    page_num = max(numbers)
                    results['all_pages'].append(page_num)
                    results['details'].append({
                        'text': text,
                        'number': page_num,
                        'confidence': block['confidence'],
                        'bbox': block['bbox']
                    })
        
        # 找出最大頁數（通常是總頁數）
        if results['all_pages']:
            results['max_pages'] = max(results['all_pages'])
        
        return results
    
    def extract_counts(self, keywords: List[str] = ['次', '張', '张']) -> Dict[str, Any]:
        """
        提取計數資訊（如列印次數、張數等）
        
        Args:
            keywords: 計數關鍵字列表
        
        Returns:
            包含計數資訊的字典
        """
        results = {
            'all_counts': [],
            'total_count': 0,
            'details': []
        }
        
        for block in self.text_blocks:
            text = block['text']
            
            if any(kw in text for kw in keywords):
                numbers = self.extract_numbers(text)
                
                if numbers:
                    count = max(numbers)
                    results['all_counts'].append(count)
                    results['details'].append({
                        'text': text,
                        'number': count,
                        'confidence': block['confidence'],
                        'bbox': block['bbox']
                    })
        
        if results['all_counts']:
            results['total_count'] = sum(results['all_counts'])
        
        return results
    
    def extract_dates(self) -> List[Dict[str, Any]]:
        """
        提取日期資訊
        
        Returns:
            包含日期的文字區塊列表
        """
        # 日期模式：YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY 等
        patterns = [
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # 2023-12-08
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # 12/08/2023
            r'\d{4}年\d{1,2}月\d{1,2}日',    # 2023年12月8日
        ]
        
        results = []
        for pattern in patterns:
            matches = self.extract_by_regex(pattern)
            results.extend(matches)
        
        return results
    
    def extract_times(self) -> List[Dict[str, Any]]:
        """
        提取時間資訊
        
        Returns:
            包含時間的文字區塊列表
        """
        # 時間模式：HH:MM, HH:MM:SS
        pattern = r'\d{1,2}:\d{2}(:\d{2})?'
        return self.extract_by_regex(pattern)
    
    def extract_ids(self, prefix: str = '') -> List[Dict[str, Any]]:
        """
        提取 ID 或編號
        
        Args:
            prefix: ID 前綴（如 'NC', 'ID' 等）
        
        Returns:
            包含 ID 的文字區塊列表
        """
        if prefix:
            pattern = f'{prefix}[A-Z0-9]+'
        else:
            # 通用 ID 模式：連續的大寫字母+數字
            pattern = r'[A-Z]{2,}\d+'
        
        return self.extract_by_regex(pattern)
    
    def extract_by_position(self, 
                           x_range: Optional[Tuple[int, int]] = None,
                           y_range: Optional[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        """
        根據位置範圍提取文字
        
        Args:
            x_range: X 座標範圍 (min, max)
            y_range: Y 座標範圍 (min, max)
        
        Returns:
            在指定位置範圍內的文字區塊
        """
        results = []
        
        for block in self.text_blocks:
            bbox = block['bbox']
            x = bbox[0][0]
            y = bbox[0][1]
            
            x_match = True if x_range is None else (x_range[0] <= x <= x_range[1])
            y_match = True if y_range is None else (y_range[0] <= y <= y_range[1])
            
            if x_match and y_match:
                results.append({
                    'text': block['text'],
                    'position': (x, y),
                    'confidence': block['confidence'],
                    'bbox': bbox
                })
        
        return results
    
    # ==================== 高級提取方法 ====================
    
    def extract_with_conditions(self,
                                keyword: Optional[str] = None,
                                pattern: Optional[str] = None,
                                min_confidence: float = 0.0,
                                x_range: Optional[Tuple[int, int]] = None,
                                y_range: Optional[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        """
        使用多個條件組合提取文字
        
        Args:
            keyword: 關鍵字
            pattern: 正則表達式模式
            min_confidence: 最低信心度
            x_range: X 座標範圍
            y_range: Y 座標範圍
        
        Returns:
            符合所有條件的文字區塊
        """
        results = []
        
        for block in self.text_blocks:
            text = block['text']
            confidence = block['confidence']
            bbox = block['bbox']
            x, y = bbox[0][0], bbox[0][1]
            
            # 檢查信心度
            if confidence < min_confidence:
                continue
            
            # 檢查關鍵字
            if keyword and keyword not in text:
                continue
            
            # 檢查正則表達式
            if pattern and not re.search(pattern, text):
                continue
            
            # 檢查位置
            if x_range and not (x_range[0] <= x <= x_range[1]):
                continue
            if y_range and not (y_range[0] <= y <= y_range[1]):
                continue
            
            results.append({
                'text': text,
                'confidence': confidence,
                'position': (x, y),
                'bbox': bbox
            })
        
        return results
    
    def extract_all_text(self, min_confidence: float = 0.0) -> List[str]:
        """
        提取所有文字內容
        
        Args:
            min_confidence: 最低信心度閾值
        
        Returns:
            文字列表
        """
        return [block['text'] for block in self.text_blocks 
                if block['confidence'] >= min_confidence]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        取得 OCR 結果摘要
        
        Returns:
            摘要資訊字典
        """
        if not self.text_blocks:
            return {'total_blocks': 0}
        
        confidences = [b['confidence'] for b in self.text_blocks]
        
        return {
            'total_blocks': len(self.text_blocks),
            'avg_confidence': sum(confidences) / len(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'high_confidence_blocks': sum(1 for c in confidences if c > 0.9),
            'rotation_angle': self.data.get('rotation_angle', 0.0),
            'preprocessing_method': self.data.get('preprocessing_method', 'none')
        }


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='文字提取工具 - 從 OCR 結果中提取特定文字和數據',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 提取頁數資訊
  %(prog)s --input result.json --extract pages
  
  # 提取所有文字
  %(prog)s --input result.json --extract all
  
  # 使用關鍵字搜尋
  %(prog)s --input result.json --keyword "系統"
  
  # 使用正則表達式
  %(prog)s --input result.json --regex "\\d{4}年"
  
  # 查看摘要
  %(prog)s --input result.json --summary
        """
    )
    
    parser.add_argument('--input', '-i', required=True, 
                       help='OCR 結果 JSON 檔案路徑')
    parser.add_argument('--extract', '-e', 
                       choices=['pages', 'counts', 'dates', 'times', 'ids', 'all'],
                       help='提取特定類型的資料')
    parser.add_argument('--keyword', '-k', help='搜尋關鍵字')
    parser.add_argument('--regex', '-r', help='正則表達式模式')
    parser.add_argument('--min-confidence', type=float, default=0.0,
                       help='最低信心度閾值 (0.0-1.0)')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='顯示 OCR 結果摘要')
    parser.add_argument('--output', '-o', help='輸出結果到 JSON 檔案')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='顯示詳細資訊')
    
    args = parser.parse_args()
    
    # 初始化提取器
    extractor = TextExtractor(args.input, verbose=args.verbose)
    
    results = {}
    
    # 顯示摘要
    if args.summary:
        summary = extractor.get_summary()
        print("\n" + "=" * 60)
        print("OCR 結果摘要")
        print("=" * 60)
        print(f"總文字區塊數: {summary['total_blocks']}")
        print(f"平均信心度: {summary['avg_confidence']*100:.2f}%")
        print(f"信心度範圍: {summary['min_confidence']*100:.2f}% - {summary['max_confidence']*100:.2f}%")
        print(f"高信心度區塊 (>90%): {summary['high_confidence_blocks']}")
        print(f"旋轉角度: {summary['rotation_angle']}°")
        print(f"預處理方法: {summary['preprocessing_method']}")
        results['summary'] = summary
    
    # 提取特定類型資料
    if args.extract:
        print("\n" + "=" * 60)
        print(f"提取 [{args.extract}] 資料")
        print("=" * 60)
        
        if args.extract == 'pages':
            data = extractor.extract_pages()
            print(f"\n找到 {len(data['details'])} 個頁數資訊:")
            for item in data['details']:
                print(f"  • {item['text']:20s} → {item['number']:4d} 頁 "
                      f"(信心度: {item['confidence']*100:.1f}%)")
            if data['max_pages']:
                print(f"\n📊 最大頁數: {data['max_pages']} 頁")
            results['pages'] = data
        
        elif args.extract == 'counts':
            data = extractor.extract_counts()
            print(f"\n找到 {len(data['details'])} 個計數資訊:")
            for item in data['details']:
                print(f"  • {item['text']:20s} → {item['number']}")
            if data['total_count']:
                print(f"\n📊 總計: {data['total_count']}")
            results['counts'] = data
        
        elif args.extract == 'dates':
            data = extractor.extract_dates()
            print(f"\n找到 {len(data)} 個日期:")
            for item in data:
                print(f"  • {item['text']} (匹配: {item['matches']})")
            results['dates'] = data
        
        elif args.extract == 'times':
            data = extractor.extract_times()
            print(f"\n找到 {len(data)} 個時間:")
            for item in data:
                print(f"  • {item['text']} (匹配: {item['matches']})")
            results['times'] = data
        
        elif args.extract == 'ids':
            data = extractor.extract_ids()
            print(f"\n找到 {len(data)} 個 ID/編號:")
            for item in data:
                print(f"  • {item['text']} (匹配: {item['matches']})")
            results['ids'] = data
        
        elif args.extract == 'all':
            data = extractor.extract_all_text(min_confidence=args.min_confidence)
            print(f"\n找到 {len(data)} 個文字區塊:")
            for i, text in enumerate(data, 1):
                print(f"  {i:3d}. {text}")
            results['all_text'] = data
    
    # 關鍵字搜尋
    if args.keyword:
        print("\n" + "=" * 60)
        print(f"搜尋關鍵字: [{args.keyword}]")
        print("=" * 60)
        data = extractor.extract_by_keyword(args.keyword)
        print(f"\n找到 {len(data)} 個匹配:")
        for item in data:
            print(f"  • {item['text']} (信心度: {item['confidence']*100:.1f}%)")
        results['keyword_search'] = data
    
    # 正則表達式搜尋
    if args.regex:
        print("\n" + "=" * 60)
        print(f"正則表達式: [{args.regex}]")
        print("=" * 60)
        data = extractor.extract_by_regex(args.regex)
        print(f"\n找到 {len(data)} 個匹配:")
        for item in data:
            print(f"  • {item['text']} → 匹配: {item['matches']}")
        results['regex_search'] = data
    
    # 輸出到檔案
    if args.output and results:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 結果已儲存至: {args.output}")
    
    if not (args.summary or args.extract or args.keyword or args.regex):
        parser.print_help()


if __name__ == '__main__':
    main()
