#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 識別器工具包裝
整合 4_OCR_Recognition 到 Pipeline
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 加入 4_OCR_Recognition 到路徑
SCRIPT_DIR = Path(__file__).parent
OCR_TOOL_DIR = SCRIPT_DIR.parent.parent.parent / "4_OCR_Recognition"
sys.path.insert(0, str(OCR_TOOL_DIR))

try:
    from ocr_parser import OCRParser
except ImportError as e:
    print(f"✗ 無法載入 ocr_parser: {e}")
    print(f"  OCR 工具路徑: {OCR_TOOL_DIR}")
    OCRParser = None


class OCRRecognizer:
    """OCR 識別器包裝器"""
    
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
            use_gpu: 是否使用 GPU
            high_sensitivity: 高敏感度模式
            convert_fullwidth: 全形轉半形
            verbose: 詳細輸出
        """
        if OCRParser is None:
            raise ImportError("無法載入 OCRParser，請檢查 4_OCR_Recognition 是否存在")
        
        self.verbose = verbose
        
        if verbose:
            print("正在初始化 OCR 識別器...")
        
        self.parser = OCRParser(
            lang=lang,
            use_gpu=use_gpu,
            high_sensitivity=high_sensitivity,
            verbose=verbose,
            convert_fullwidth=convert_fullwidth
        )
        
        if verbose:
            print("✓ OCR 識別器初始化完成")
    
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
            
            # 執行 OCR
            result = self.parser.recognize(str(image_path))
            
            if not result.get("success"):
                error = result.get("error", "未知錯誤")
                return False, result, f"識別失敗: {error}"
            
            # 如果指定輸出路徑，儲存 JSON
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 準備輸出資料
                output_data = {
                    "source_image": str(image_path.name),
                    "total_blocks": result["total_blocks"],
                    "text_blocks": result["text_blocks"],
                    "full_text": "\n".join([block["text"] for block in result["text_blocks"]])
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            blocks_count = result.get("total_blocks", 0)
            return True, result, f"成功識別 {blocks_count} 個文字塊"
            
        except Exception as e:
            return False, {}, f"處理失敗: {str(e)}"
    
    def recognize_batch(self,
                       input_dir: Path,
                       output_dir: Path,
                       image_extensions: List[str] = None) -> Tuple[int, int, List[Dict]]:
        """
        批次識別圖片
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
            image_extensions: 圖片副檔名清單
            
        Returns:
            (成功數量, 總數量, 結果列表)
        """
        if image_extensions is None:
            image_extensions = ['.png', '.jpg', '.jpeg']
        
        # 建立輸出目錄
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集所有圖片
        image_files = []
        for ext in image_extensions:
            image_files.extend(sorted(input_dir.glob(f"*{ext}")))
        
        if not image_files:
            return 0, 0, []
        
        if self.verbose:
            print(f"\n找到 {len(image_files)} 張圖片")
        
        # 批次處理
        results = []
        success_count = 0
        
        for image_path in image_files:
            # 產生輸出檔名 (page_001.png -> page_001.json)
            output_filename = image_path.stem + '.json'
            output_path = output_dir / output_filename
            
            if self.verbose:
                print(f"  處理: {image_path.name}...", end=' ')
            
            success, result, message = self.recognize_single(
                image_path,
                output_path
            )
            
            if success:
                success_count += 1
                if self.verbose:
                    blocks = result.get("total_blocks", 0)
                    print(f"✓ ({blocks} 個文字塊)")
            else:
                if self.verbose:
                    print(f"✗ {message}")
            
            results.append({
                "file": image_path.name,
                "output": output_filename if success else None,
                "success": success,
                "message": message,
                "blocks": result.get("total_blocks", 0) if success else 0
            })
        
        return success_count, len(image_files), results


# 匯出
__all__ = ['OCRRecognizer']
