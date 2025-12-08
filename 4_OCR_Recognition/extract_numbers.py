#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 OCR 結果中動態提取特定數字的多種方法
示範如何提取「1250頁」這類數據
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple


class NumberExtractor:
    """數字提取器 - 從 OCR 結果中提取特定格式的數字"""
    
    def __init__(self, json_path: str):
        """初始化，載入 OCR 結果"""
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.text_blocks = self.data.get('text_blocks', [])
    
    # ========== 方法 1: 關鍵字精確匹配 ==========
    def extract_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        方法1: 通過關鍵字精確匹配
        
        優點: 簡單直接
        缺點: 必須知道完整的關鍵字
        
        Args:
            keyword: 要匹配的關鍵字（如「頁」、「页」）
        
        Returns:
            包含該關鍵字的所有文字區塊
        """
        results = []
        for block in self.text_blocks:
            if keyword in block['text']:
                results.append({
                    'text': block['text'],
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        return results
    
    # ========== 方法 2: 正則表達式模式匹配 ==========
    def extract_by_regex(self, pattern: str) -> List[Dict[str, Any]]:
        """
        方法2: 使用正則表達式匹配模式
        
        優點: 靈活，可以匹配複雜模式
        缺點: 需要了解正則表達式
        
        Args:
            pattern: 正則表達式模式
                例如: r'\d+\s*[頁页]' 匹配「數字+頁」
                     r'\d+\s*[張张]' 匹配「數字+張」
        
        Returns:
            匹配的文字區塊和提取的數字
        """
        results = []
        regex = re.compile(pattern)
        
        for block in self.text_blocks:
            text = block['text']
            matches = regex.findall(text)
            if matches:
                results.append({
                    'text': text,
                    'matches': matches,
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        return results
    
    # ========== 方法 3: 提取純數字 ==========
    def extract_number_from_text(self, text: str) -> Optional[int]:
        """
        從文字中提取數字
        
        Args:
            text: 包含數字的文字（如「1250页」）
        
        Returns:
            提取的數字（如 1250）
        """
        # 移除所有非數字字符
        numbers = re.findall(r'\d+', text)
        if numbers:
            # 如果有多個數字，取最大的（通常是主要數字）
            return int(max(numbers, key=lambda x: int(x)))
        return None
    
    # ========== 方法 4: 語意搜尋（模糊匹配）==========
    def extract_by_semantic(self, keywords: List[str], 
                          context_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        方法4: 語意搜尋，支援多個關鍵字和上下文
        
        優點: 容錯性高，支援同義詞
        缺點: 可能產生誤匹配
        
        Args:
            keywords: 主要關鍵字列表（如 ['頁', '页', 'page']）
            context_keywords: 上下文關鍵字（如 ['印', '列印', '剩餘']）
        
        Returns:
            匹配的文字區塊
        """
        results = []
        
        for block in self.text_blocks:
            text = block['text']
            
            # 檢查是否包含主要關鍵字
            has_keyword = any(kw in text for kw in keywords)
            
            if has_keyword:
                # 如果指定了上下文關鍵字，檢查附近區塊
                if context_keywords:
                    # 這裡可以檢查前後區塊是否包含上下文關鍵字
                    # 簡化版本：先加入結果
                    pass
                
                results.append({
                    'text': text,
                    'number': self.extract_number_from_text(text),
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        
        return results
    
    # ========== 方法 5: 位置定位 ==========
    def extract_by_position(self, x_range: Optional[Tuple[int, int]] = None,
                           y_range: Optional[Tuple[int, int]] = None,
                           contains_digit: bool = True) -> List[Dict[str, Any]]:
        """
        方法5: 根據位置範圍提取
        
        優點: 適合固定格式的表單
        缺點: 需要知道具體位置
        
        Args:
            x_range: X 座標範圍 (min, max)
            y_range: Y 座標範圍 (min, max)
            contains_digit: 是否必須包含數字
        
        Returns:
            在指定位置範圍內的文字區塊
        """
        results = []
        
        for block in self.text_blocks:
            bbox = block['bbox']
            x = bbox[0][0]  # 左上角 X 座標
            y = bbox[0][1]  # 左上角 Y 座標
            
            # 檢查位置
            x_match = True if x_range is None else (x_range[0] <= x <= x_range[1])
            y_match = True if y_range is None else (y_range[0] <= y <= y_range[1])
            
            # 檢查是否包含數字
            digit_match = True if not contains_digit else bool(re.search(r'\d', block['text']))
            
            if x_match and y_match and digit_match:
                results.append({
                    'text': block['text'],
                    'position': (x, y),
                    'confidence': block['confidence'],
                    'bbox': bbox
                })
        
        return results
    
    # ========== 方法 6: 組合條件篩選 ==========
    def extract_by_conditions(self, 
                             keyword: Optional[str] = None,
                             pattern: Optional[str] = None,
                             min_confidence: float = 0.0,
                             min_digits: int = 1) -> List[Dict[str, Any]]:
        """
        方法6: 組合多個條件進行篩選
        
        優點: 最靈活，可以組合多種條件
        缺點: 需要仔細調整參數
        
        Args:
            keyword: 關鍵字（可選）
            pattern: 正則表達式模式（可選）
            min_confidence: 最低信心度閾值
            min_digits: 最少數字位數
        
        Returns:
            符合所有條件的文字區塊
        """
        results = []
        
        for block in self.text_blocks:
            text = block['text']
            confidence = block['confidence']
            
            # 檢查信心度
            if confidence < min_confidence:
                continue
            
            # 檢查關鍵字
            if keyword and keyword not in text:
                continue
            
            # 檢查正則表達式
            if pattern and not re.search(pattern, text):
                continue
            
            # 檢查數字位數
            numbers = re.findall(r'\d+', text)
            if numbers:
                max_number = max(numbers, key=len)
                if len(max_number) < min_digits:
                    continue
            else:
                continue
            
            results.append({
                'text': text,
                'number': int(max_number),
                'confidence': confidence,
                'bbox': block['bbox']
            })
        
        return results


def demo_all_methods():
    """示範所有提取方法"""
    
    print("=" * 80)
    print("OCR 數字提取示範 - 以「1250頁」為例")
    print("=" * 80)
    
    # 初始化提取器
    extractor = NumberExtractor('result/result_fuji.json')
    
    # ========== 方法 1: 關鍵字匹配 ==========
    print("\n【方法 1】關鍵字精確匹配")
    print("-" * 80)
    results = extractor.extract_by_keyword('页')
    print(f"找到 {len(results)} 個包含「页」的區塊：")
    for r in results:
        print(f"  • {r['text']} (信心度: {r['confidence']*100:.2f}%)")
    
    # ========== 方法 2: 正則表達式 ==========
    print("\n【方法 2】正則表達式模式匹配")
    print("-" * 80)
    
    # 示範不同的正則表達式
    patterns = {
        r'\d+\s*[頁页]': '數字+頁',
        r'\d{3,}\s*[頁页]': '3位以上數字+頁',
        r'1\d{3}\s*[頁页]': '1開頭的4位數+頁',
    }
    
    for pattern, desc in patterns.items():
        results = extractor.extract_by_regex(pattern)
        print(f"\n模式: {pattern} ({desc})")
        print(f"找到 {len(results)} 個匹配:")
        for r in results:
            print(f"  • {r['text']} - 匹配: {r['matches']}")
    
    # ========== 方法 3: 提取數字 ==========
    print("\n【方法 3】從文字中提取純數字")
    print("-" * 80)
    test_texts = ['1250页', '294页', '95 6 页', 'ABC 123 頁 456']
    for text in test_texts:
        number = extractor.extract_number_from_text(text)
        print(f"  {text:20s} → {number}")
    
    # ========== 方法 4: 語意搜尋 ==========
    print("\n【方法 4】語意搜尋（多關鍵字）")
    print("-" * 80)
    results = extractor.extract_by_semantic(
        keywords=['頁', '页', 'page'],
        context_keywords=None
    )
    print(f"找到 {len(results)} 個結果:")
    for r in results:
        print(f"  • {r['text']} → 數字: {r['number']} (信心度: {r['confidence']*100:.2f}%)")
    
    # ========== 方法 5: 位置定位 ==========
    print("\n【方法 5】根據位置範圍提取")
    print("-" * 80)
    results = extractor.extract_by_position(
        x_range=(200, 300),  # X 座標 200-300 之間
        y_range=(170, 220),  # Y 座標 170-220 之間
        contains_digit=True
    )
    print(f"在指定位置範圍內找到 {len(results)} 個包含數字的區塊:")
    for r in results:
        print(f"  • {r['text']} at 位置 {r['position']}")
    
    # ========== 方法 6: 組合條件 ==========
    print("\n【方法 6】組合多個條件篩選")
    print("-" * 80)
    results = extractor.extract_by_conditions(
        keyword='页',
        pattern=r'\d{3,}',  # 至少3位數字
        min_confidence=0.8,  # 信心度 > 80%
        min_digits=3  # 至少3位數
    )
    print(f"符合所有條件的結果:")
    for r in results:
        print(f"  • {r['text']} → {r['number']} (信心度: {r['confidence']*100:.2f}%)")
    
    # ========== 實際應用：提取「1250頁」==========
    print("\n" + "=" * 80)
    print("【實際應用】提取「1250頁」的最佳方法")
    print("=" * 80)
    
    # 方法組合：關鍵字 + 4位數字 + 高信心度
    results = extractor.extract_by_conditions(
        keyword='页',
        pattern=r'1\d{3}',  # 1開頭的4位數
        min_confidence=0.9,
        min_digits=4
    )
    
    if results:
        target = results[0]
        print(f"\n✅ 成功提取:")
        print(f"   原始文字: {target['text']}")
        print(f"   提取數字: {target['number']}")
        print(f"   信心度: {target['confidence']*100:.2f}%")
        print(f"   位置: {target['bbox']}")
    else:
        print("\n⚠️  未找到符合條件的結果")


if __name__ == '__main__':
    demo_all_methods()
