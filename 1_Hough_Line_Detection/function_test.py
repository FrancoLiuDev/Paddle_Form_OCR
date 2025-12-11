#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
霍夫線條檢測功能測試腳本

此腳本包含所有相關函數的測試功能，包括：
- preprocess_image_for_line_detection: 專門的線條檢測預處理
- detect_and_fill_text_regions: 文字區域檢測和填黑
- detect_optimal_angle: 最佳角度檢測
- apply_angle_correction: 角度修正
- visualize_line_detection: 線條檢測可視化

作者: GitHub Copilot
日期: 2025-12-11
"""

import os
import sys
import cv2
import numpy as np
import argparse
from typing import Tuple, Optional

# 導入主要的預處理函數
from preprocess_hough import (
    preprocess_image_for_line_detection,
    detect_and_fill_text_regions,
    detect_optimal_angle,
    apply_angle_correction,
    visualize_line_detection,
    preprocess_image
)


class FunctionTester:
    """霍夫線條檢測功能測試類"""
    
    def __init__(self, output_dir: str = "result_test"):
        """
        初始化測試器
        
        Args:
            output_dir: 測試結果輸出目錄
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"測試結果將儲存至: {self.output_dir}")
    
    def test_line_detection_preprocessing(self, image_path: str, verbose: bool = True) -> str:
        """
        測試線條檢測專用預處理函數
        
        Args:
            image_path: 輸入圖像路徑
            verbose: 是否顯示詳細輸出
            
        Returns:
            輸出檔案路徑
        """
        print("\n" + "="*50)
        print("測試: preprocess_image_for_line_detection")
        print("="*50)
        
        # 讀取圖像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"無法讀取圖像: {image_path}")
        
        if verbose:
            print(f"輸入圖像: {image_path}")
            print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
        
        # 轉換為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 執行線條檢測預處理
        processed = preprocess_image_for_line_detection(gray)
        
        # 保存結果
        basename = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(self.output_dir, f"{basename}_line_detection.png")
        cv2.imwrite(output_path, processed)
        
        if verbose:
            print(f"結果已儲存: {output_path}")
        
        return output_path
    
    def test_text_region_filling(self, image_path: str, verbose: bool = True) -> str:
        """
        測試文字區域檢測和填黑功能
        
        Args:
            image_path: 輸入圖像路徑
            verbose: 是否顯示詳細輸出
            
        Returns:
            輸出檔案路徑
        """
        print("\n" + "="*50)
        print("測試: detect_and_fill_text_regions")
        print("="*50)
        
        # 讀取圖像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"無法讀取圖像: {image_path}")
        
        # 轉換為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if verbose:
            print(f"輸入圖像: {image_path}")
            print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
        
        # 執行文字區域填黑
        filled = detect_and_fill_text_regions(gray)
        
        # 保存結果
        basename = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(self.output_dir, f"{basename}_text_filled.png")
        cv2.imwrite(output_path, filled)
        
        if verbose:
            print(f"結果已儲存: {output_path}")
        
        return output_path
    
    def test_angle_detection(self, image_path: str, verbose: bool = True) -> Optional[float]:
        """
        測試角度檢測功能
        
        Args:
            image_path: 輸入圖像路徑
            verbose: 是否顯示詳細輸出
            
        Returns:
            檢測到的角度（如果失敗則返回 None）
        """
        print("\n" + "="*50)
        print("測試: detect_optimal_angle")
        print("="*50)
        
        # 讀取圖像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"無法讀取圖像: {image_path}")
        
        if verbose:
            print(f"輸入圖像: {image_path}")
            print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
        
        # 檢測角度
        angle = detect_optimal_angle(image, verbose=verbose)
        
        if verbose:
            if angle is not None:
                print(f"檢測結果: 角度={angle:.2f}°")
            else:
                print("檢測結果: 無法檢測到有效角度")
        
        return angle
    
    def test_angle_correction(self, image_path: str, angle: Optional[float] = None, verbose: bool = True) -> str:
        """
        測試角度修正功能
        
        Args:
            image_path: 輸入圖像路徑
            angle: 指定修正角度，None表示自動檢測
            verbose: 是否顯示詳細輸出
            
        Returns:
            輸出檔案路徑
        """
        print("\n" + "="*50)
        print("測試: apply_angle_correction")
        print("="*50)
        
        # 讀取圖像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"無法讀取圖像: {image_path}")
        
        if verbose:
            print(f"輸入圖像: {image_path}")
            print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
        
        # 如果沒有指定角度，先檢測
        if angle is None:
            angle, _ = detect_optimal_angle(image, verbose=verbose)
        
        if verbose:
            print(f"使用角度: {angle}°")
        
        # 執行角度修正
        corrected = apply_angle_correction(image, angle, verbose=verbose)
        
        # 保存結果
        basename = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(self.output_dir, f"{basename}_corrected_{angle:.1f}deg.png")
        cv2.imwrite(output_path, corrected)
        
        if verbose:
            print(f"結果已儲存: {output_path}")
        
        return output_path
    
    def test_line_visualization(self, image_path: str, degree_limit: Optional[float] = None, verbose: bool = True) -> str:
        """
        測試線條檢測可視化功能
        
        Args:
            image_path: 輸入圖像路徑
            degree_limit: 角度限制（±度數）
            verbose: 是否顯示詳細輸出
            
        Returns:
            輸出檔案路徑
        """
        print("\n" + "="*50)
        print("測試: visualize_line_detection")
        print("="*50)
        
        # 讀取圖像
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"無法讀取圖像: {image_path}")
        
        if verbose:
            print(f"輸入圖像: {image_path}")
            print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
            if degree_limit:
                print(f"角度限制: ±{degree_limit}°")
        
        # 設定輸出路徑
        basename = os.path.splitext(os.path.basename(image_path))[0]
        if degree_limit:
            output_path = os.path.join(self.output_dir, f"{basename}_lines_{degree_limit}deg.png")
        else:
            output_path = os.path.join(self.output_dir, f"{basename}_lines_all.png")
        
        # 執行線條可視化
        result = visualize_line_detection(image, output_path, degree_limit=degree_limit)
        
        if verbose:
            print(f"結果已儲存: {output_path}")
        
        return output_path
    
    def test_complete_pipeline(self, image_path: str, verbose: bool = True) -> dict:
        """
        測試完整的處理流程
        
        Args:
            image_path: 輸入圖像路徑
            verbose: 是否顯示詳細輸出
            
        Returns:
            包含所有結果路徑的字典
        """
        print("\n" + "="*60)
        print("完整流程測試")
        print("="*60)
        
        results = {}
        
        # 1. 線條檢測預處理
        results['line_detection'] = self.test_line_detection_preprocessing(image_path, verbose)
        
        # 2. 文字區域填黑
        results['text_filled'] = self.test_text_region_filling(image_path, verbose)
        
        # 3. 角度檢測
        angle = self.test_angle_detection(image_path, verbose)
        results['angle'] = angle
        
        # 4. 角度修正
        results['corrected'] = self.test_angle_correction(image_path, angle, verbose)
        
        # 5. 線條可視化（全部線條）
        results['lines_all'] = self.test_line_visualization(image_path, None, verbose)
        
        # 6. 線條可視化（10度限制）
        results['lines_10deg'] = self.test_line_visualization(image_path, 10.0, verbose)
        
        if verbose:
            print("\n" + "="*60)
            print("完整測試完成！")
            print("="*60)
            print("生成的檔案:")
            for key, value in results.items():
                if isinstance(value, str) and os.path.exists(value):
                    print(f"  {key}: {value}")
                elif key == 'angle':
                    print(f"  {key}: {value}°" if value is not None else f"  {key}: None")
        
        return results


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='霍夫線條檢測功能測試工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output-dir', '-o', default='result_test', help='輸出目錄（預設：result_test）')
    parser.add_argument('--test', '-t', choices=[
        'line_detection', 'text_filled', 'angle_detection', 
        'angle_correction', 'line_visualization', 'complete'
    ], default='complete', help='要執行的測試類型（預設：complete）')
    parser.add_argument('--angle', type=float, help='指定角度修正值（用於 angle_correction 測試）')
    parser.add_argument('--degree-limit', type=float, help='線條可視化的角度限制（用於 line_visualization 測試）')
    parser.add_argument('--verbose', '-v', action='store_true', help='顯示詳細輸出')
    
    args = parser.parse_args()
    
    # 檢查輸入檔案
    if not os.path.exists(args.input):
        print(f"錯誤: 找不到輸入檔案 {args.input}")
        return 1
    
    # 建立測試器
    tester = FunctionTester(args.output_dir)
    
    try:
        # 執行指定的測試
        if args.test == 'line_detection':
            tester.test_line_detection_preprocessing(args.input, args.verbose)
        elif args.test == 'text_filled':
            tester.test_text_region_filling(args.input, args.verbose)
        elif args.test == 'angle_detection':
            tester.test_angle_detection(args.input, args.verbose)
        elif args.test == 'angle_correction':
            tester.test_angle_correction(args.input, args.angle, args.verbose)
        elif args.test == 'line_visualization':
            tester.test_line_visualization(args.input, args.degree_limit, args.verbose)
        elif args.test == 'complete':
            tester.test_complete_pipeline(args.input, args.verbose)
        
        print(f"\n測試完成！結果已儲存至 {args.output_dir}/")
        return 0
        
    except Exception as e:
        print(f"測試失敗: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
