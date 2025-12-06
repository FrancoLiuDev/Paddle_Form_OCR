#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 表單識別工具
使用 PaddleOCR 進行離線文字識別
可整合多種預處理方法
"""

import argparse
import json
import os
from pathlib import Path
from paddleocr import PaddleOCR
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple


class OCRParser:
    """OCR 表單識別器"""
    
    def __init__(self, lang: str = 'ch', use_gpu: bool = False, 
                 high_sensitivity: bool = False, verbose: bool = False):
        """
        初始化 OCR 識別器
        
        Args:
            lang: 語言類型 ('ch'=中文, 'en'=英文)
            use_gpu: 是否使用 GPU
            high_sensitivity: 高敏感度模式（識別更多文字）
            verbose: 詳細輸出
        """
        self.verbose = verbose
        
        if verbose:
            print(f"正在初始化 PaddleOCR（語言: {lang}, GPU: {use_gpu}）...")
        
        # 根據敏感度設置參數
        if high_sensitivity:
            det_db_thresh = 0.2
            det_db_box_thresh = 0.4
            det_db_unclip_ratio = 2.0
        else:
            det_db_thresh = 0.3
            det_db_box_thresh = 0.5
            det_db_unclip_ratio = 1.6
        
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False,
            det_db_thresh=det_db_thresh,
            det_db_box_thresh=det_db_box_thresh,
            det_db_unclip_ratio=det_db_unclip_ratio
        )
        
        if verbose:
            print("✓ PaddleOCR 初始化完成")
    
    def recognize(self, image_path: str) -> Dict[str, Any]:
        """
        識別圖像中的文字
        
        Returns:
            結果字典，包含識別的文字和位置
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"找不到檔案: {image_path}"}
        
        if self.verbose:
            print(f"\n正在識別: {image_path}")
        
        # OCR 識別
        result = self.ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return {
                "success": False,
                "error": "未檢測到文字",
                "text_blocks": []
            }
        
        # 解析結果
        text_blocks = []
        for line in result[0]:
            bbox = line[0]  # 座標
            text_info = line[1]  # (文字, 置信度)
            
            text_blocks.append({
                "text": text_info[0],
                "confidence": float(text_info[1]),
                "bbox": bbox
            })
        
        if self.verbose:
            print(f"✓ 檢測到 {len(text_blocks)} 個文字塊")
        
        return {
            "success": True,
            "total_blocks": len(text_blocks),
            "text_blocks": text_blocks
        }
    
    def visualize(self, image_path: str, result: Dict[str, Any], output_path: str):
        """
        可視化識別結果
        """
        if not result.get("success"):
            print("無法可視化：識別失敗")
            return
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"無法讀取圖像: {image_path}")
            return
        
        # 繪製文字框
        for block in result.get("text_blocks", []):
            bbox = block["bbox"]
            points = np.array(bbox, dtype=np.int32)
            
            # 綠色框
            cv2.polylines(image, [points], True, (0, 255, 0), 2)
            
            # 顯示文字
            text = block["text"]
            confidence = block["confidence"]
            
            # 在框上方顯示文字和置信度
            x, y = int(bbox[0][0]), int(bbox[0][1])
            label = f"{text[:20]} ({confidence:.2f})"
            cv2.putText(image, label, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 儲存
        cv2.imwrite(output_path, image)
        
        if self.verbose:
            print(f"✓ 可視化結果已儲存至: {output_path}")


def preprocess_with_method(image_path: str, method: str, model_path: str = None, 
                          verbose: bool = False) -> Tuple[str, float]:
    """
    使用指定方法預處理圖像
    
    Returns:
        (processed_path, rotation_angle)
    """
    temp_dir = os.path.join(os.path.dirname(image_path), ".preprocessed")
    os.makedirs(temp_dir, exist_ok=True)
    
    output_path = os.path.join(temp_dir, f"preprocessed_{os.path.basename(image_path)}")
    
    if method == 'hough':
        # 使用霍夫直線檢測
        if verbose:
            print("使用霍夫直線檢測預處理...")
        
        try:
            # 嘗試導入模組
            import sys
            sys.path.insert(0, '../1_Hough_Line_Detection')
            from preprocess_hough import preprocess_image
            
            image = cv2.imread(image_path)
            processed, angle = preprocess_image(image, enable_rotation=True, verbose=verbose)
            cv2.imwrite(output_path, processed)
            
            return output_path, angle
        except ImportError:
            print("警告: 找不到霍夫直線檢測模組，使用原始圖像")
            return image_path, 0.0
    
    elif method == 'pca':
        # 使用 PCA
        if verbose:
            print("使用 PCA 預處理...")
        
        try:
            import sys
            sys.path.insert(0, '../2_Scikit_Learn_PCA')
            from preprocess_pca import preprocess_image
            
            image = cv2.imread(image_path)
            processed, angle = preprocess_image(image, enable_rotation=True, 
                                               verbose=verbose, debug=False)
            cv2.imwrite(output_path, processed)
            
            return output_path, angle
        except ImportError:
            print("警告: 找不到 PCA 模組，使用原始圖像")
            return image_path, 0.0
    
    elif method == 'dl':
        # 使用深度學習
        if verbose:
            print("使用深度學習預處理...")
        
        try:
            import sys
            sys.path.insert(0, '../3_MobileNetV3_DL')
            from preprocess_dl import preprocess_image
            
            image = cv2.imread(image_path)
            processed, angle = preprocess_image(image, model_path=model_path, 
                                               enable_rotation=True, verbose=verbose)
            cv2.imwrite(output_path, processed)
            
            return output_path, angle
        except ImportError:
            print("警告: 找不到深度學習模組，使用原始圖像")
            return image_path, 0.0
    
    else:
        # 無預處理
        return image_path, 0.0


def main():
    parser = argparse.ArgumentParser(description='OCR 表單識別工具')
    parser.add_argument('--image', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', help='輸出 JSON 檔案路徑')
    parser.add_argument('--visualize', '-v', help='可視化輸出路徑')
    parser.add_argument('--lang', default='ch', choices=['ch', 'en', 'ch_en'], 
                       help='識別語言')
    parser.add_argument('--use-gpu', action='store_true', help='使用 GPU 加速')
    parser.add_argument('--high-sensitivity', action='store_true', 
                       help='高敏感度模式')
    parser.add_argument('--preprocess', action='store_true', help='啟用預處理')
    parser.add_argument('--method', choices=['hough', 'pca', 'dl'], default='pca',
                       help='預處理方法')
    parser.add_argument('--model', help='深度學習模型路徑（method=dl 時使用）')
    parser.add_argument('--verbose', action='store_true', help='詳細輸出')
    
    args = parser.parse_args()
    
    # 預處理
    image_path = args.image
    rotation_angle = 0.0
    preprocessing_method = 'none'
    
    if args.preprocess:
        preprocessing_method = args.method
        image_path, rotation_angle = preprocess_with_method(
            args.image, args.method, args.model, args.verbose
        )
    
    # OCR 識別
    ocr_parser = OCRParser(
        lang=args.lang,
        use_gpu=args.use_gpu,
        high_sensitivity=args.high_sensitivity,
        verbose=args.verbose
    )
    
    result = ocr_parser.recognize(image_path)
    
    # 添加預處理資訊
    result["rotation_angle"] = rotation_angle
    result["preprocessing_method"] = preprocessing_method
    
    # 可視化
    if args.visualize and result.get("success"):
        ocr_parser.visualize(args.image, result, args.visualize)
    
    # 輸出結果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        if args.verbose:
            print(f"\n✓ 結果已儲存至: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 顯示摘要
    if args.verbose and result.get("success"):
        print(f"\n=== 識別摘要 ===")
        print(f"預處理方法: {preprocessing_method}")
        print(f"旋轉角度: {rotation_angle:.2f}°")
        print(f"文字塊數量: {result.get('total_blocks', 0)}")


if __name__ == '__main__':
    main()
