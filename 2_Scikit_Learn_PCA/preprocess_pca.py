#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scikit-Learn PCA 預處理工具
使用主成分分析檢測圖像旋轉角度
"""

import cv2
import numpy as np
import argparse
import os
from typing import Tuple
from sklearn.decomposition import PCA


def detect_angle_by_pca(image: np.ndarray, verbose: bool = False, debug: bool = False) -> Tuple[float, float]:
    """
    使用 PCA 檢測圖像旋轉角度
    
    返回:
        angle: 檢測到的角度（度）
        confidence: 置信度分數
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    
    # 邊緣檢測
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 獲取邊緣點座標
    points = np.column_stack(np.where(edges > 0))
    
    if len(points) < 10:
        if verbose:
            print("  邊緣點過少，無法進行 PCA 分析")
        return 0.0, 0.0
    
    if debug:
        print(f"  檢測到 {len(points)} 個邊緣點")
    
    # PCA 分析
    pca = PCA(n_components=2)
    pca.fit(points)
    
    # 獲取主成分
    components = pca.components_
    explained_variance = pca.explained_variance_ratio_
    
    if debug:
        print(f"  主成分方差比: {explained_variance}")
        print(f"  第一主成分: {components[0]}")
        print(f"  第二主成分: {components[1]}")
    
    # 計算主成分的角度
    angle_rad = np.arctan2(components[0][0], components[0][1])
    angle_deg = np.degrees(angle_rad)
    
    # 置信度：第一主成分與第二主成分的方差比
    confidence = explained_variance[0] / (explained_variance[0] + explained_variance[1])
    
    if verbose:
        print(f"  PCA 檢測角度: {angle_deg:.2f}°")
        print(f"  置信度: {confidence:.2%}")
    
    # 標準化角度到 [-45, 45] 範圍
    # 因為文字通常接近水平方向
    if angle_deg > 45:
        angle_deg -= 90
    elif angle_deg < -45:
        angle_deg += 90
    
    if verbose:
        print(f"  標準化後角度: {angle_deg:.2f}°")
    
    return angle_deg, confidence


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """旋轉圖像"""
    if abs(angle) < 0.1:
        return image
    
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # 計算旋轉矩陣
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # 執行旋轉
    rotated = cv2.warpAffine(image, matrix, (w, h), 
                            flags=cv2.INTER_CUBIC, 
                            borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def auto_rotate_by_pca(image: np.ndarray, verbose: bool = False, debug: bool = False) -> Tuple[np.ndarray, float]:
    """
    基於 PCA 自動旋轉圖像
    
    返回:
        rotated_image: 旋轉後的圖像
        rotation_angle: 旋轉的角度
    """
    if verbose:
        print("\n=== PCA 旋轉分析 ===")
    
    angle, confidence = detect_angle_by_pca(image, verbose, debug)
    
    if abs(angle) < 0.5:
        if verbose:
            print("角度過小，無需旋轉")
        return image, 0.0
    
    if confidence < 0.6:
        if verbose:
            print(f"置信度過低 ({confidence:.2%})，建議檢查圖像質量")
    
    if verbose:
        print(f"應用旋轉: {angle:.2f}°")
    
    rotated = rotate_image(image, angle)
    return rotated, angle


def preprocess_image(image: np.ndarray, enable_rotation: bool = True, 
                    verbose: bool = False, debug: bool = False) -> Tuple[np.ndarray, float]:
    """
    完整的圖像預處理流程
    
    返回:
        processed_image: 處理後的圖像
        rotation_angle: 旋轉的角度
    """
    rotation_angle = 0.0
    
    # 1. 自動旋轉
    if enable_rotation:
        image, rotation_angle = auto_rotate_by_pca(image, verbose, debug)
    
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
    parser = argparse.ArgumentParser(description='Scikit-Learn PCA 預處理工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', required=True, help='輸出圖像路徑')
    parser.add_argument('--no-rotation', action='store_true', help='停用自動旋轉')
    parser.add_argument('--verbose', '-v', action='store_true', help='顯示詳細輸出')
    parser.add_argument('--debug', '-d', action='store_true', help='顯示除錯資訊')
    
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
    
    # 預處理
    processed, rotation_angle = preprocess_image(
        image, 
        enable_rotation=not args.no_rotation,
        verbose=args.verbose,
        debug=args.debug
    )
    
    # 儲存結果
    cv2.imwrite(args.output, processed)
    
    if args.verbose:
        print(f"\n處理完成！")
        print(f"旋轉角度: {rotation_angle:.2f}°")
        print(f"輸出檔案: {args.output}")
    else:
        print(f"已儲存至: {args.output} (旋轉 {rotation_angle:.2f}°)")


if __name__ == '__main__':
    main()
