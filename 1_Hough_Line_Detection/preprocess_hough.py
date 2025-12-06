#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
霍夫直線檢測預處理工具
使用霍夫變換檢測圖像中的線條方向，自動旋轉圖像
"""

import cv2
import numpy as np
import argparse
import os
from typing import Tuple, List, Optional


def detect_angle_by_lines(image: np.ndarray, verbose: bool = False) -> Tuple[int, float]:
    """
    使用霍夫直線檢測來判斷圖像需要旋轉的角度
    
    返回:
        rotation_angle: 需要旋轉的角度 (0, 90, 180, 270)
        confidence: 置信度分數
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    
    # 邊緣檢測
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫直線檢測
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    
    if lines is None:
        if verbose:
            print("  未檢測到線條，返回 0° 旋轉")
        return 0, 0.0
    
    # 統計各方向的線條數量
    angle_counts = {
        0: 0,    # 水平線
        45: 0,   # 45度斜線
        90: 0,   # 垂直線
        135: 0   # 135度斜線
    }
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # 計算線條角度
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        
        # 分類線條方向
        if angle < 22.5 or angle > 157.5:
            angle_counts[0] += 1
        elif 22.5 <= angle < 67.5:
            angle_counts[45] += 1
        elif 67.5 <= angle < 112.5:
            angle_counts[90] += 1
        elif 112.5 <= angle < 157.5:
            angle_counts[135] += 1
    
    if verbose:
        print(f"  線條統計: 水平={angle_counts[0]}, 45°={angle_counts[45]}, " +
              f"垂直={angle_counts[90]}, 135°={angle_counts[135]}")
    
    # 計算文字投影方差來輔助判斷
    scores = {}
    for test_angle in [0, 90, 180, 270]:
        rotated = rotate_image(image.copy(), test_angle)
        rotated_gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY) if len(rotated.shape) == 3 else rotated
        
        # 計算水平投影方差（文字行應該產生高方差）
        horizontal_projection = np.sum(rotated_gray < 200, axis=1)
        variance = np.var(horizontal_projection)
        
        # 結合線條數量和投影方差
        line_score = angle_counts.get((test_angle % 180), 0)
        scores[test_angle] = variance * (1 + line_score * 0.1)
        
        if verbose:
            print(f"  角度 {test_angle}°: 投影方差={variance:.1f}, 線條加權分數={scores[test_angle]:.1f}")
    
    # 選擇分數最高的角度
    best_angle = max(scores, key=scores.get)
    confidence = scores[best_angle] / (sum(scores.values()) + 1e-6)
    
    if verbose:
        print(f"  最佳旋轉角度: {best_angle}°, 置信度: {confidence:.2%}")
    
    return best_angle, confidence


def visualize_line_detection(image: np.ndarray, output_path: str) -> np.ndarray:
    """
    可視化霍夫直線檢測結果，用紅色標記檢測到的線條
    """
    result = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    
    # 邊緣檢測
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫直線檢測
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # 用紅色標記線條
            cv2.line(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        print(f"  檢測到 {len(lines)} 條線，已用紅色標記")
    else:
        print("  未檢測到線條")
    
    # 儲存可視化結果
    if output_path:
        vis_path = output_path.replace('.', '_lines.')
        cv2.imwrite(vis_path, result)
        print(f"  線條可視化已儲存至: {vis_path}")
    
    return result


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """旋轉圖像"""
    if angle == 0:
        return image
    
    h, w = image.shape[:2]
    
    if angle in [90, 270]:
        # 90度或270度旋轉
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        else:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    else:
        # 任意角度旋轉
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), 
                             flags=cv2.INTER_CUBIC, 
                             borderMode=cv2.BORDER_REPLICATE)


def auto_rotate_by_content(image: np.ndarray, verbose: bool = False) -> Tuple[np.ndarray, int]:
    """
    基於內容自動旋轉圖像
    
    返回:
        rotated_image: 旋轉後的圖像
        rotation_angle: 旋轉的角度
    """
    if verbose:
        print("\n=== 霍夫直線檢測旋轉分析 ===")
    
    rotation_angle, confidence = detect_angle_by_lines(image, verbose)
    
    if rotation_angle == 0:
        if verbose:
            print("無需旋轉")
        return image, 0
    
    if verbose:
        print(f"應用旋轉: {rotation_angle}°")
    
    rotated = rotate_image(image, rotation_angle)
    return rotated, rotation_angle


def preprocess_image(image: np.ndarray, enable_rotation: bool = True, verbose: bool = False) -> Tuple[np.ndarray, int]:
    """
    完整的圖像預處理流程
    
    返回:
        processed_image: 處理後的圖像
        rotation_angle: 旋轉的角度
    """
    rotation_angle = 0
    
    # 1. 自動旋轉
    if enable_rotation:
        image, rotation_angle = auto_rotate_by_content(image, verbose)
    
    # 2. 降噪
    if verbose:
        print("\n=== 圖像增強 ===")
        print("  應用降噪...")
    image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    # 3. 灰階轉換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 4. 對比度增強
    if verbose:
        print("  增強對比度...")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 5. 銳化
    if verbose:
        print("  應用銳化...")
    kernel = np.array([[-1, -1, -1],
                      [-1,  9, -1],
                      [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # 轉回彩色以便後續處理
    result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    
    if verbose:
        print("\n預處理完成！")
    
    return result, rotation_angle


def main():
    parser = argparse.ArgumentParser(description='霍夫直線檢測預處理工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', required=True, help='輸出圖像路徑')
    parser.add_argument('--show-lines', action='store_true', help='顯示檢測到的線條（紅色標記）')
    parser.add_argument('--no-rotation', action='store_true', help='停用自動旋轉')
    parser.add_argument('--verbose', '-v', action='store_true', help='顯示詳細輸出')
    
    args = parser.parse_args()
    
    # 讀取圖像
    if not os.path.exists(args.input):
        print(f"錯誤: 找不到輸入檔案 {args.input}")
        return
    
    image = cv2.imread(args.input)
    if image is None:
        print(f"錯誤: 無法讀取圖像 {args.input}")
        return
    
    if args.verbose:
        print(f"讀取圖像: {args.input}")
        print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 線條可視化模式
    if args.show_lines:
        print("\n=== 線條檢測可視化 ===")
        visualize_line_detection(image, args.output)
        return
    
    # 預處理
    processed, rotation_angle = preprocess_image(
        image, 
        enable_rotation=not args.no_rotation,
        verbose=args.verbose
    )
    
    # 儲存結果
    cv2.imwrite(args.output, processed)
    
    if args.verbose:
        print(f"\n處理完成！")
        print(f"旋轉角度: {rotation_angle}°")
        print(f"輸出檔案: {args.output}")
    else:
        print(f"已儲存至: {args.output} (旋轉 {rotation_angle}°)")


if __name__ == '__main__':
    main()
