#!/usr/bin/env python3
"""
智能欄位偵測器 - 使用多種策略自動推測欄位內容

策略包括：
1. 模糊匹配 (Fuzzy Matching) - 容錯字串比對
2. 語義分析 (Semantic Analysis) - 理解文字含義
3. 位置推理 (Position Inference) - 根據版面位置推測
4. 模式識別 (Pattern Recognition) - 識別常見格式
5. 上下文分析 (Context Analysis) - 分析相鄰文字
"""

import json
import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class SmartFieldDetector:
    """智能欄位偵測器"""
    
    def __init__(self, json_file: str):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.text_blocks = self.data.get('text_blocks', [])
    
    # ============ 策略 1: 模糊匹配 ============
    
    def fuzzy_match(self, text: str, target: str, threshold: float = 0.6) -> float:
        """
        計算兩個字串的相似度 (0-1)
        
        Args:
            text: 待比對字串
            target: 目標字串
            threshold: 相似度門檻
        
        Returns:
            相似度分數
        """
        # 使用 SequenceMatcher 計算相似度
        similarity = SequenceMatcher(None, text, target).ratio()
        return similarity
    
    def find_by_fuzzy_match(self, target: str, threshold: float = 0.6) -> List[Dict]:
        """
        使用模糊匹配尋找相似的欄位
        
        Example:
            target = "總印張數"
            可能找到: "印张数" (相似度 0.67)
        """
        results = []
        
        for i, block in enumerate(self.text_blocks):
            text = block['text'].strip()
            similarity = self.fuzzy_match(text, target)
            
            if similarity >= threshold:
                results.append({
                    'index': i,
                    'text': text,
                    'similarity': similarity,
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results
    
    # ============ 策略 2: 語義分析 ============
    
    def semantic_search(self, concept: str, keywords: List[str]) -> List[Dict]:
        """
        語義搜尋：根據概念和相關關鍵字搜尋
        
        Example:
            concept = "印表機型號"
            keywords = ["型號", "型号", "機型", "model", "名稱", "名称"]
        """
        results = []
        
        for i, block in enumerate(self.text_blocks):
            text = block['text'].strip()
            
            # 檢查是否包含任何關鍵字
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    results.append({
                        'index': i,
                        'text': text,
                        'matched_keyword': keyword,
                        'confidence': block['confidence'],
                        'bbox': block['bbox']
                    })
                    break
        
        return results
    
    # ============ 策略 3: 位置推理 ============
    
    def find_value_by_position(self, field_index: int, direction: str = 'right') -> Optional[Dict]:
        """
        根據欄位位置推測對應的值
        
        Args:
            field_index: 欄位的索引
            direction: 搜尋方向 ('right', 'below', 'above')
        """
        if field_index >= len(self.text_blocks):
            return None
        
        field = self.text_blocks[field_index]
        field_bbox = field['bbox']
        field_x = field_bbox[1][0]  # 右邊 x
        field_y = (field_bbox[0][1] + field_bbox[2][1]) / 2  # 中心 y
        
        candidates = []
        
        for i, block in enumerate(self.text_blocks):
            if i == field_index:
                continue
            
            bbox = block['bbox']
            x = bbox[0][0]
            y = (bbox[0][1] + bbox[2][1]) / 2
            
            if direction == 'right':
                # 在右邊且 y 座標接近（同一行）
                if x > field_x and abs(y - field_y) < 20:
                    distance = x - field_x
                    candidates.append({
                        'index': i,
                        'text': block['text'],
                        'confidence': block['confidence'],
                        'distance': distance,
                        'y_diff': abs(y - field_y)
                    })
            
            elif direction == 'below':
                # 在下方且 x 座標接近（同一列）
                if y > field_y and abs(x - field_x) < 20:
                    distance = y - field_y
                    candidates.append({
                        'index': i,
                        'text': block['text'],
                        'confidence': block['confidence'],
                        'distance': distance
                    })
        
        # 選擇最接近的
        if candidates:
            candidates.sort(key=lambda x: (x.get('y_diff', 0), x['distance']))
            return candidates[0]
        
        return None
    
    # ============ 策略 4: 模式識別 ============
    
    def recognize_pattern(self, pattern_type: str) -> List[Dict]:
        """
        識別特定格式的文字
        
        Args:
            pattern_type: 模式類型
                - 'number': 數字 (如 1250)
                - 'page': 頁數 (如 1250頁, 294页)
                - 'serial': 序號 (如 NC7003677)
                - 'model': 型號 (如 C325, ApeosC325)
                - 'date': 日期 (如 2024/12/08)
        """
        patterns = {
            'number': r'\d+',
            'page': r'\d+\s*[頁页]',
            'serial': r'[A-Z]{2}\d{7,}',
            'model': r'[A-Z]\d{3,}|Apeos[A-Z]\d{3,}',
            'date': r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            'time': r'\d{1,2}:\d{2}',
            'ip': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        }
        
        if pattern_type not in patterns:
            return []
        
        pattern = patterns[pattern_type]
        results = []
        
        for i, block in enumerate(self.text_blocks):
            text = block['text'].strip()
            matches = re.findall(pattern, text)
            
            if matches:
                results.append({
                    'index': i,
                    'text': text,
                    'matches': matches,
                    'confidence': block['confidence'],
                    'bbox': block['bbox']
                })
        
        return results
    
    # ============ 策略 5: 上下文分析 ============
    
    def analyze_context(self, index: int, window: int = 3) -> Dict:
        """
        分析指定索引周圍的上下文
        
        Args:
            index: 要分析的文字區塊索引
            window: 前後各多少個區塊
        """
        context = {
            'target': self.text_blocks[index],
            'before': [],
            'after': []
        }
        
        # 前面的區塊
        for i in range(max(0, index - window), index):
            context['before'].append({
                'index': i,
                'text': self.text_blocks[i]['text'],
                'confidence': self.text_blocks[i]['confidence']
            })
        
        # 後面的區塊
        for i in range(index + 1, min(len(self.text_blocks), index + window + 1)):
            context['after'].append({
                'index': i,
                'text': self.text_blocks[i]['text'],
                'confidence': self.text_blocks[i]['confidence']
            })
        
        return context
    
    # ============ 整合策略 ============
    
    def smart_extract(self, field_name: str, hints: Dict = None) -> Dict:
        """
        智能提取：結合多種策略自動推測欄位
        
        Args:
            field_name: 要提取的欄位名稱
            hints: 提示資訊 {
                'keywords': [...],      # 可能的關鍵字
                'pattern': 'number',    # 值的格式
                'position': 'right',    # 值的位置
                'fuzzy_threshold': 0.6  # 模糊匹配門檻
            }
        
        Returns:
            提取結果和信心度
        """
        if hints is None:
            hints = {}
        
        result = {
            'field_name': field_name,
            'found': False,
            'strategies_used': [],
            'candidates': []
        }
        
        # 策略 1: 先嘗試精確匹配關鍵字
        if 'keywords' in hints:
            semantic_results = self.semantic_search(field_name, hints['keywords'])
            if semantic_results:
                result['strategies_used'].append('semantic_search')
                for sr in semantic_results[:3]:  # 取前 3 個
                    # 找對應的值
                    value = self.find_value_by_position(
                        sr['index'], 
                        hints.get('position', 'right')
                    )
                    if value:
                        result['candidates'].append({
                            'field': sr,
                            'value': value,
                            'strategy': 'semantic + position'
                        })
        
        # 策略 2: 如果沒找到，使用模糊匹配
        if not result['candidates']:
            fuzzy_threshold = hints.get('fuzzy_threshold', 0.6)
            fuzzy_results = self.find_by_fuzzy_match(field_name, fuzzy_threshold)
            if fuzzy_results:
                result['strategies_used'].append('fuzzy_match')
                for fr in fuzzy_results[:3]:
                    value = self.find_value_by_position(
                        fr['index'],
                        hints.get('position', 'right')
                    )
                    if value:
                        result['candidates'].append({
                            'field': fr,
                            'value': value,
                            'strategy': 'fuzzy + position'
                        })
        
        # 策略 3: 如果有指定模式，使用模式識別
        if 'pattern' in hints and not result['candidates']:
            pattern_results = self.recognize_pattern(hints['pattern'])
            if pattern_results:
                result['strategies_used'].append('pattern_recognition')
                for pr in pattern_results[:3]:
                    result['candidates'].append({
                        'value': pr,
                        'strategy': 'pattern_only'
                    })
        
        # 選擇最佳候選
        if result['candidates']:
            result['found'] = True
            # 優先選擇信心度最高的
            best = max(result['candidates'], 
                      key=lambda x: x['value'].get('confidence', 0))
            result['best_match'] = best
        
        return result


def demo():
    """示範智能偵測功能"""
    
    detector = SmartFieldDetector('../4_OCR_Recognition/result/result_fuji.json')
    
    print('='*70)
    print('🤖 智能欄位偵測器 - 示範')
    print('='*70)
    print()
    
    # 示範 1: 模糊匹配
    print('📌 示範 1: 模糊匹配 - 即使有錯字也能找到')
    print('-'*70)
    target = "總印張數"
    print(f'搜尋目標: "{target}"')
    results = detector.find_by_fuzzy_match(target, threshold=0.5)
    print(f'找到 {len(results)} 個相似結果：')
    for r in results[:3]:
        print(f'  • "{r["text"]}" (相似度: {r["similarity"]:.2%})')
    print()
    
    # 示範 2: 語義搜尋
    print('📌 示範 2: 語義搜尋 - 用概念和關鍵字搜尋')
    print('-'*70)
    concept = "印表機型號"
    keywords = ["型號", "型号", "名稱", "名称", "機型", "model"]
    print(f'搜尋概念: "{concept}"')
    print(f'關鍵字: {keywords}')
    results = detector.semantic_search(concept, keywords)
    print(f'找到 {len(results)} 個結果：')
    for r in results[:3]:
        print(f'  • "{r["text"]}" (匹配: {r["matched_keyword"]})')
    print()
    
    # 示範 3: 模式識別
    print('📌 示範 3: 模式識別 - 自動識別特定格式')
    print('-'*70)
    print('搜尋格式: 頁數 (如 1250頁)')
    results = detector.recognize_pattern('page')
    print(f'找到 {len(results)} 個頁數：')
    for r in results[:5]:
        print(f'  • "{r["text"]}" → 匹配: {r["matches"]}')
    print()
    
    print('搜尋格式: 序號 (如 NC7003677)')
    results = detector.recognize_pattern('serial')
    print(f'找到 {len(results)} 個序號：')
    for r in results[:3]:
        print(f'  • "{r["text"]}" → 匹配: {r["matches"]}')
    print()
    
    # 示範 4: 智能提取（整合策略）
    print('📌 示範 4: 智能提取 - 自動選擇最佳策略')
    print('-'*70)
    
    # 提取印表機名稱
    result = detector.smart_extract(
        '印表機名稱',
        hints={
            'keywords': ['印表機名稱', '印表機名称', '印表名稱', '印表名称', '名稱', '名称'],
            'position': 'right',
            'fuzzy_threshold': 0.5
        }
    )
    
    print(f'欄位: 印表機名稱')
    print(f'找到: {"是" if result["found"] else "否"}')
    print(f'使用策略: {", ".join(result["strategies_used"])}')
    if result['found']:
        best = result['best_match']
        print(f'欄位文字: "{best["field"]["text"]}"')
        print(f'值: "{best["value"]["text"]}"')
        print(f'信心度: {best["value"]["confidence"]*100:.1f}%')
    print()
    
    # 提取總印張數
    result = detector.smart_extract(
        '總印張數',
        hints={
            'keywords': ['總印張數', '总印张数', '印張數', '印张数'],
            'pattern': 'page',
            'position': 'right',
            'fuzzy_threshold': 0.5
        }
    )
    
    print(f'欄位: 總印張數')
    print(f'找到: {"是" if result["found"] else "否"}')
    print(f'使用策略: {", ".join(result["strategies_used"])}')
    if result['found']:
        best = result['best_match']
        print(f'欄位文字: "{best["field"]["text"]}"')
        print(f'值: "{best["value"]["text"]}"')
        print(f'信心度: {best["value"]["confidence"]*100:.1f}%')
    print()
    
    print('='*70)
    print('✨ 智能偵測可以處理：')
    print('  • OCR 錯字/漏字')
    print('  • 不同的表達方式')
    print('  • 自動識別數字、日期等格式')
    print('  • 根據版面位置推測關聯')
    print('='*70)


if __name__ == '__main__':
    demo()
