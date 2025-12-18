#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的 PaddleOCR 測試腳本（新版 API）
"""

from paddleocr import PaddleOCR
import json
import sys

def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else '../11_PDF_Pipeline/meta/images_rotated/page_006.png'
    
    print(f"正在識別: {image_path}")
    print("初始化 PaddleOCR...")
    
    # 新版 PaddleOCR 3.x API
    ocr = PaddleOCR(
        lang='ch',  # 語言
        use_textline_orientation=True,  # 文字方向檢測
        # GPU 由 PaddlePaddle 自動檢測，無需指定
    )
    
    print("開始 OCR 識別...")
    result = ocr.predict(image_path)
    
    print(f"\n=== 結果結構 ===")
    print(f"類型: {type(result)}")
    print(f"頁數: {len(result) if result else 0}")
    
    if result and len(result) > 0:
        print(f"\n第一頁:")
        print(f"  - 類型: {type(result[0])}")
        print(f"  - 文字塊數量: {len(result[0]) if result[0] else 0}")
        
        # OCRResult 對象，使用 .json 屬性獲取結果
        ocr_result = result[0]
        result_json = ocr_result.json
        
        # 提取文字框和識別結果
        dt_polys = result_json.get('dt_polys', [])
        rec_texts = result_json.get('rec_text', [])
        rec_scores = result_json.get('rec_score', [])
        
        print(f"\n=== OCR 識別結果 ===")
        print(f"文字塊數量: {len(rec_texts)}")
        print(f"文字框數量: {len(dt_polys)}")
        print(f"置信度數量: {len(rec_scores)}")
        
        # 顯示前 5 個識別結果
        print(f"\n=== 前 5 個文字塊 ===")
        for i in range(min(5, len(rec_texts))):
            text = rec_texts[i] if i < len(rec_texts) else ""
            score = rec_scores[i] if i < len(rec_scores) else 0
            poly = dt_polys[i] if i < len(dt_polys) else []
            
            print(f"\n{i+1}. 文字: {text}")
            print(f"   置信度: {score:.4f}")
            print(f"   位置: {poly[:2] if len(poly) >= 2 else poly}")  # 只顯示前兩個角
        
        # 顯示所有識別的文字
        print(f"\n=== 所有識別文字 ===")
        for i, text in enumerate(rec_texts, 1):
            print(f"{i}. {text}")

if __name__ == '__main__':
    main()
