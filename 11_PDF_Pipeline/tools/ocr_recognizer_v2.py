#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 識別器 v2 - 使用新版 PaddleOCR 3.x API
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from paddleocr import PaddleOCR


class OCRRecognizerV2:
    """OCR 識別器 - 新版 PaddleOCR API"""
    
    def __init__(self, 
                 lang: str = 'ch',
                 use_gpu: bool = False,
                 high_sensitivity: bool = False,
                 convert_fullwidth: bool = True,
                 verbose: bool = False):
        """
        初始化 OCR 識別器
        
        Args:
            lang: 語言 ('ch' 中文, 'en' 英文)
            use_gpu: 是否使用 GPU（注意：新版 PaddleOCR 會自動檢測）
            high_sensitivity: 高敏感度模式
            convert_fullwidth: 全形轉半形
            verbose: 詳細輸出
        """
        self.verbose = verbose
        self.convert_fullwidth = convert_fullwidth
        
        if verbose:
            print(f"正在初始化 PaddleOCR（語言: {lang}, GPU: {use_gpu}）...")
        
        # 新版 PaddleOCR 3.x API 參數（僅使用支援的參數）
        ocr_params = {
            'lang': lang,
            'use_textline_orientation': False,  # 文字方向檢測（關閉以加速）
        }
        
        # 根據敏感度設置參數
        if high_sensitivity:
            ocr_params['text_det_thresh'] = 0.2
            ocr_params['text_det_box_thresh'] = 0.4
            ocr_params['text_det_unclip_ratio'] = 2.0
        else:
            ocr_params['text_det_thresh'] = 0.3
            ocr_params['text_det_box_thresh'] = 0.5
            ocr_params['text_det_unclip_ratio'] = 1.6
        
        # 注意：新版 PaddleOCR 移除了 use_gpu 參數
        # GPU 使用由 PaddlePaddle 自動檢測
        
        self.ocr = PaddleOCR(**ocr_params)
        
        if verbose:
            print("✓ PaddleOCR 初始化完成")
    
    @staticmethod
    def fullwidth_to_halfwidth(text: str) -> str:
        """將全形字符轉換為半形"""
        result = []
        for char in text:
            code = ord(char)
            # 全形空格
            if code == 0x3000:
                result.append(chr(0x0020))
            # 全形字符範圍
            elif 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            # 特殊全形標點
            elif char in '，。！？：；「」『』【】（）':
                halfwidth_map = {
                    '，': ',', '。': '.', '！': '!', '？': '?',
                    '：': ':', '；': ';', '「': '"', '」': '"',
                    '『': "'", '』': "'", '【': '[', '】': ']',
                    '（': '(', '）': ')'
                }
                result.append(halfwidth_map.get(char, char))
            else:
                result.append(char)
        return ''.join(result)
    
    def recognize_single(self, 
                        image_path: Path,
                        output_path: Optional[Path] = None) -> Tuple[bool, Dict, str]:
        """
        識別單張圖片
        
        Args:
            image_path: 圖片路徑
            output_path: JSON 輸出路徑（可選）
            
        Returns:
            (成功, 結果字典, 訊息)
        """
        try:
            if not image_path.exists():
                return False, {}, f"找不到圖片: {image_path}"
            
            if self.verbose:
                print(f"正在識別: {image_path}")
            
            # 執行 OCR（使用新版 API）
            result = self.ocr.predict(str(image_path))
            
            if not result or len(result) == 0:
                return False, {}, "OCR 返回空結果"
            
            # 解析結果（新版 API 返回 OCRResult 對象）
            ocr_result = result[0]
            result_json = ocr_result.json['res']
            
            rec_texts = result_json.get('rec_texts', [])
            rec_scores = result_json.get('rec_scores', [])
            dt_polys = result_json.get('dt_polys', [])
            
            if not rec_texts:
                return False, {}, "未檢測到文字"
            
            # 組織輸出資料
            text_blocks = []
            for text, score, poly in zip(rec_texts, rec_scores, dt_polys):
                # 全形轉半形
                if self.convert_fullwidth:
                    converted_text = self.fullwidth_to_halfwidth(text)
                else:
                    converted_text = text
                
                block = {
                    "text": converted_text,
                    "confidence": float(score),
                    "bbox": poly
                }
                
                # 如果有轉換，記錄原始文字
                if self.convert_fullwidth and text != converted_text:
                    block["original_text"] = text
                
                text_blocks.append(block)
            
            result_data = {
                "success": True,
                "total_blocks": len(text_blocks),
                "text_blocks": text_blocks,
                "full_text": "\n".join([block["text"] for block in text_blocks])
            }
            
            # 如果指定輸出路徑，儲存 JSON
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                output_json = {
                    "source_image": str(image_path.name),
                    "total_blocks": result_data["total_blocks"],
                    "text_blocks": result_data["text_blocks"],
                    "full_text": result_data["full_text"]
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_json, f, ensure_ascii=False, indent=2)
            
            if self.verbose:
                print(f"✓ 檢測到 {len(text_blocks)} 個文字塊")
            
            return True, result_data, "識別成功"
            
        except Exception as e:
            return False, {}, f"識別過程出錯: {str(e)}"
    
    def recognize_batch(self,
                       input_dir: Path,
                       output_dir: Path,
                       pattern: str = "*.png",
                       start_page: int = 1) -> Tuple[int, int, List[Dict]]:
        """
        批次識別
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            pattern: 檔案匹配模式
            start_page: 開始處理的頁碼（從 1 開始，預設 1）
            
        Returns:
            (成功數量, 總數量, 結果列表)
        """
        # 確保輸出目錄存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 取得所有圖片
        all_image_files = sorted(input_dir.glob(pattern))
        
        if not all_image_files:
            if self.verbose:
                print(f"✗ 在 {input_dir} 找不到符合 {pattern} 的圖片")
            return 0, 0, []
        
        # 根據 start_page 過濾圖片
        if start_page > 1:
            image_files = all_image_files[start_page - 1:]
            if self.verbose:
                print(f"找到 {len(all_image_files)} 張圖片，從第 {start_page} 頁開始處理（處理 {len(image_files)} 張）")
        else:
            image_files = all_image_files
            if self.verbose:
                print(f"找到 {len(image_files)} 張圖片")
        
        success_count = 0
        results = []
        
        for i, image_path in enumerate(image_files, 1):
            if self.verbose:
                print(f"[{i}/{len(image_files)}] 處理: {image_path.name}")
            
            # 產生輸出檔名
            output_path = output_dir / f"{image_path.stem}.json"
            
            # 識別
            success, result_data, message = self.recognize_single(
                image_path,
                output_path
            )
            
            if success:
                success_count += 1
                results.append({
                    "image": str(image_path.name),
                    "success": True,
                    "blocks": result_data["total_blocks"],
                    "output": str(output_path.name)
                })
                if self.verbose:
                    print(f"  ✓ 成功，檢測到 {result_data['total_blocks']} 個文字塊")
            else:
                results.append({
                    "image": str(image_path.name),
                    "success": False,
                    "error": message
                })
                if self.verbose:
                    print(f"  ✗ 失敗: {message}")
        
        return success_count, len(image_files), results


# 為了兼容性，建立別名
OCRRecognizer = OCRRecognizerV2
