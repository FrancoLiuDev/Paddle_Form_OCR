#!/usr/bin/env python3
"""
OCR 語意校正工具
使用多種策略修正 OCR 誤識別的文字
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from difflib import get_close_matches


class SemanticCorrector:
    """OCR 語意校正器"""
    
    def __init__(self):
        # 策略 1: 常見誤識別字典（形近字）
        self.similar_chars = {
            # 常見 OCR 錯誤
            '稠': '稱',  # 印表機名稱 → 印表機名稠
            '赋': '號',  # 序號 → 序赋
            '碍': '時',  # 時間 → 碍間
            '妨': '防',  # 防火牆 → 妨火牆
            '枪': '槍',  # 槍械 → 枪械
            '栽': '載',  # 下載 → 下栽
            '飩': '沌',  # 混沌 → 混飩
            '0': 'O',   # 數字 0 vs 字母 O（依上下文）
            'O': '0',   # 字母 O vs 數字 0（依上下文）
            '1': 'I',   # 數字 1 vs 字母 I（依上下文）
            'I': '1',   # 字母 I vs 數字 1（依上下文）
        }
        
        # 策略 2: 領域專用詞典（正確的專業術語）
        self.domain_terms = {
            '印表機': ['印表機名稱', '印表機語言', '印表機型號', '印表機設定'],
            '序號': ['序號', '序列號', '機器序號'],
            '張數': ['總印張數', '彩色印張數', '黑白印張數', '列印張數'],
            '系統': ['系統設定', '系統資訊', '系統管理'],
            '網路': ['網路設定', '網路位址', '網路協定'],
            '日期': ['日期時間', '列印日期', '系統日期'],
        }
        
        # 策略 3: 上下文規則（根據前後文判斷）
        self.context_rules = [
            # (pattern, wrong, correct, description)
            (r'印表.*名稠', '稠', '稱', '印表機名稱中的稠應為稱'),
            (r'序赋', '赋', '號', '序號中的赋應為號'),
            (r'日期.*特碍', '碍', '時', '日期時間中的碍應為時'),
            (r'黑白印次', '次', '張數', '印張數中的次應為張數'),
        ]
        
        # 策略 4: 數字/字母混淆檢測
        self.number_letter_patterns = {
            'serial': r'[A-Z]{2}\d+',  # 序號格式：兩個大寫字母 + 數字
            'ip': r'\d+\.\d+\.\d+\.\d+',  # IP 格式
            'date': r'\d{2,4}[/-]\d{1,2}[/-]\d{1,2}',  # 日期格式
            'model': r'[A-Z]\d{3}',  # 型號格式
        }
    
    def correct_similar_chars(self, text: str, context: str = '') -> Tuple[str, List[str]]:
        """
        策略 1: 修正形近字
        
        Args:
            text: 要修正的文字
            context: 上下文（可選）
        
        Returns:
            (修正後的文字, 修正記錄列表)
        """
        corrections = []
        result = text
        
        for wrong, correct in self.similar_chars.items():
            if wrong in result:
                # 檢查上下文是否支持此修正
                if context:
                    # 如果有上下文，進行更智能的判斷
                    result_with_context = result.replace(wrong, correct)
                    if self._is_valid_in_context(result_with_context, context):
                        corrections.append(f'形近字: "{wrong}" → "{correct}"')
                        result = result_with_context
                else:
                    corrections.append(f'形近字: "{wrong}" → "{correct}"')
                    result = result.replace(wrong, correct)
        
        return result, corrections
    
    def correct_domain_terms(self, text: str) -> Tuple[str, List[str]]:
        """
        策略 2: 使用領域詞典修正專業術語
        
        Returns:
            (修正後的文字, 修正記錄列表)
        """
        corrections = []
        result = text
        
        # 建立完整的術語列表
        all_terms = []
        for terms_list in self.domain_terms.values():
            all_terms.extend(terms_list)
        
        # 尋找相似的正確術語
        for term in all_terms:
            # 計算相似度
            if self._fuzzy_match(text, term, threshold=0.7):
                if text != term:
                    corrections.append(f'術語修正: "{text}" → "{term}"')
                    result = term
                    break
        
        return result, corrections
    
    def correct_by_context(self, text: str, prev_text: str = '', next_text: str = '') -> Tuple[str, List[str]]:
        """
        策略 3: 根據上下文規則修正
        
        Args:
            text: 要修正的文字
            prev_text: 前一個文字區塊
            next_text: 後一個文字區塊
        
        Returns:
            (修正後的文字, 修正記錄列表)
        """
        corrections = []
        result = text
        
        # 組合上下文
        context = f"{prev_text} {text} {next_text}"
        
        for pattern, wrong, correct, description in self.context_rules:
            if re.search(pattern, context):
                if wrong in result:
                    corrections.append(f'上下文: {description}')
                    result = result.replace(wrong, correct)
        
        return result, corrections
    
    def correct_number_letter_confusion(self, text: str, field_type: str = 'auto') -> Tuple[str, List[str]]:
        """
        策略 4: 修正數字/字母混淆
        
        Args:
            text: 要修正的文字
            field_type: 欄位類型 ('serial', 'ip', 'date', 'model', 'auto')
        
        Returns:
            (修正後的文字, 修正記錄列表)
        """
        corrections = []
        result = text
        
        # 自動偵測類型
        if field_type == 'auto':
            for ptype, pattern in self.number_letter_patterns.items():
                if re.search(pattern, text):
                    field_type = ptype
                    break
        
        # 根據類型修正
        if field_type == 'serial':
            # 序號：前兩個應該是字母，後面是數字
            if len(text) >= 3:
                # 修正前兩個字符為字母
                first_two = text[:2]
                rest = text[2:]
                
                first_two_corrected = first_two.replace('0', 'O').replace('1', 'I')
                rest_corrected = rest.replace('O', '0').replace('I', '1').replace('l', '1')
                
                result = first_two_corrected + rest_corrected
                if result != text:
                    corrections.append(f'序號格式: "{text}" → "{result}"')
        
        elif field_type == 'ip' or field_type == 'date':
            # IP 和日期應該都是數字
            result = text.replace('O', '0').replace('I', '1').replace('l', '1')
            if result != text:
                corrections.append(f'{field_type}格式: "{text}" → "{result}"')
        
        return result, corrections
    
    def correct_text(self, text: str, context: Dict = None) -> Dict:
        """
        綜合修正：應用所有策略
        
        Args:
            text: 要修正的文字
            context: 上下文資訊 {
                'prev': '前一個文字',
                'next': '後一個文字',
                'field_name': '欄位名稱',
                'field_type': '欄位類型'
            }
        
        Returns:
            修正結果字典
        """
        if context is None:
            context = {}
        
        original = text
        all_corrections = []
        
        # 應用各種策略
        text, corr1 = self.correct_similar_chars(text, context.get('field_name', ''))
        all_corrections.extend(corr1)
        
        text, corr2 = self.correct_domain_terms(text)
        all_corrections.extend(corr2)
        
        text, corr3 = self.correct_by_context(
            text,
            context.get('prev', ''),
            context.get('next', '')
        )
        all_corrections.extend(corr3)
        
        text, corr4 = self.correct_number_letter_confusion(
            text,
            context.get('field_type', 'auto')
        )
        all_corrections.extend(corr4)
        
        return {
            'original': original,
            'corrected': text,
            'changed': original != text,
            'corrections': all_corrections
        }
    
    def correct_ocr_result(self, json_file: str, output_file: str = None) -> Dict:
        """
        修正整個 OCR 結果檔案
        
        Args:
            json_file: OCR 結果 JSON 檔案
            output_file: 輸出檔案（可選）
        
        Returns:
            修正統計
        """
        # 讀取 OCR 結果
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text_blocks = data.get('text_blocks', [])
        total_corrections = 0
        correction_details = []
        
        # 逐個修正
        for i, block in enumerate(text_blocks):
            text = block['text']
            
            # 準備上下文
            context = {
                'prev': text_blocks[i-1]['text'] if i > 0 else '',
                'next': text_blocks[i+1]['text'] if i < len(text_blocks)-1 else ''
            }
            
            # 修正
            result = self.correct_text(text, context)
            
            if result['changed']:
                block['original_text'] = result['original']
                block['text'] = result['corrected']
                block['corrections'] = result['corrections']
                total_corrections += 1
                
                correction_details.append({
                    'index': i,
                    'original': result['original'],
                    'corrected': result['corrected'],
                    'corrections': result['corrections']
                })
        
        # 儲存結果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            'total_blocks': len(text_blocks),
            'corrected_blocks': total_corrections,
            'correction_rate': f'{total_corrections/len(text_blocks)*100:.1f}%' if text_blocks else '0%',
            'details': correction_details
        }
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.7) -> bool:
        """模糊匹配"""
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, text1, text2).ratio()
        return similarity >= threshold
    
    def _is_valid_in_context(self, text: str, context: str) -> bool:
        """檢查修正後的文字在上下文中是否合理"""
        # 簡單的檢查：看修正後的文字是否在領域詞典中
        for terms_list in self.domain_terms.values():
            if any(term in text for term in terms_list):
                return True
        return False


def demo():
    """示範語意校正功能"""
    
    corrector = SemanticCorrector()
    
    print('='*70)
    print('🔧 OCR 語意校正工具示範')
    print('='*70)
    print()
    
    # 測試案例
    test_cases = [
        {
            'text': '印表名稠',
            'context': {'field_name': '印表機'},
            'description': '形近字修正'
        },
        {
            'text': '序赋',
            'context': {},
            'description': '形近字修正'
        },
        {
            'text': '黑白印次',
            'context': {'prev': '彩色印張數', 'next': '294页'},
            'description': '上下文修正'
        },
        {
            'text': 'NC7OO3677',  # O 應該是 0
            'context': {'field_type': 'serial'},
            'description': '數字/字母混淆'
        },
        {
            'text': '日期/特碍',
            'context': {},
            'description': '形近字修正'
        },
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f'📌 測試 {i}: {case["description"]}')
        print(f'   原始: "{case["text"]}"')
        
        result = corrector.correct_text(case['text'], case['context'])
        
        if result['changed']:
            print(f'   ✅ 修正: "{result["corrected"]}"')
            for correction in result['corrections']:
                print(f'      • {correction}')
        else:
            print(f'   ℹ️  無需修正')
        print()
    
    # 測試完整 OCR 檔案修正
    print('='*70)
    print('📄 測試完整檔案修正')
    print('='*70)
    print()
    
    ocr_file = '../4_OCR_Recognition/result/result_fuji.json'
    output_file = '../4_OCR_Recognition/result/result_fuji_corrected.json'
    
    try:
        stats = corrector.correct_ocr_result(ocr_file, output_file)
        
        print(f'總區塊數: {stats["total_blocks"]}')
        print(f'修正區塊數: {stats["corrected_blocks"]}')
        print(f'修正率: {stats["correction_rate"]}')
        print()
        
        if stats['details']:
            print('修正詳情（前 5 個）:')
            for detail in stats['details'][:5]:
                print(f'  • 索引 {detail["index"]}: "{detail["original"]}" → "{detail["corrected"]}"')
                for corr in detail['corrections']:
                    print(f'    - {corr}')
        
        print()
        print(f'✅ 修正結果已儲存至: {output_file}')
        
    except FileNotFoundError:
        print(f'⚠️  找不到檔案: {ocr_file}')
        print('   請先執行 OCR 識別')
    
    print()
    print('='*70)
    print('✨ 示範完成')
    print('='*70)


if __name__ == '__main__':
    demo()
