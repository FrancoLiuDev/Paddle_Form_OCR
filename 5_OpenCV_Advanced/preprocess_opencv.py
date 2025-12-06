#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCV 進階角度檢測工具
結合多種 OpenCV 技術：輪廓檢測、最小外接矩形、霍夫變換、投影法
"""

import cv2
import numpy as np
import argparse
from typing import Tuple, List
import os


def detect_angle_by_contours(image: np.ndarray, verbose: bool = False) -> Tuple[float, float]:
    """
    使用輪廓檢測和最小外接矩形來檢測角度
    適合有明確邊界的文件
    
    Args:
        image: 輸入圖像
        verbose: 是否輸出詳細信息
    
    Returns:
        (angle, confidence): 角度和置信度
    """
    # 轉換為灰階
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # 二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 尋找輪廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return 0.0, 0.0
    
    # 找到最大的輪廓（假設是文檔主體）
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 計算最小外接矩形
    rect = cv2.minAreaRect(largest_contour)
    angle = rect[2]
    
    # OpenCV 的 minAreaRect 返回的角度範圍是 [-90, 0)
    # 需要調整到我們想要的範圍
    if angle < -45:
        angle = 90 + angle
    
    # 置信度基於輪廓面積與圖像面積的比例
    contour_area = cv2.contourArea(largest_contour)
    image_area = gray.shape[0] * gray.shape[1]
    confidence = min(contour_area / image_area, 1.0)
    
    if verbose:
        print(f"  輪廓數量: {len(contours)}")
        print(f"  最大輪廓面積: {contour_area:.0f}")
        print(f"  檢測角度: {angle:.2f}°")
        print(f"  置信度: {confidence:.2%}")
    
    return angle, confidence


def detect_angle_by_projection(image: np.ndarray, verbose: bool = False) -> Tuple[float, float]:
    """
    使用投影法檢測角度
    通過計算不同角度的投影方差來找出最佳角度
    
    Args:
        image: 輸入圖像
        verbose: 是否輸出詳細信息
    
    Returns:
        (angle, confidence): 角度和置信度
    """
    # 轉換為灰階
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # 二值化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 縮小圖像以提高速度
    scale = 0.5
    small = cv2.resize(binary, None, fx=scale, fy=scale)
    
    # 測試角度範圍
    angles = np.arange(-10, 10, 0.5)
    variances = []
    
    h, w = small.shape
    center = (w // 2, h // 2)
    
    for angle in angles:
        # 旋轉圖像
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(small, M, (w, h), flags=cv2.INTER_LINEAR)
        
        # 計算水平投影
        projection = np.sum(rotated, axis=1)
        
        # 計算方差（方差越大說明文字行越清晰）
        variance = np.var(projection)
        variances.append(variance)
    
    # 找出方差最大的角度
    max_idx = np.argmax(variances)
    best_angle = angles[max_idx]
    max_variance = variances[max_idx]
    
    # 置信度基於方差的相對大小
    mean_variance = np.mean(variances)
    confidence = min((max_variance - mean_variance) / mean_variance, 1.0) if mean_variance > 0 else 0.0
    
    if verbose:
        print(f"  測試角度範圍: {angles[0]:.1f}° 到 {angles[-1]:.1f}°")
        print(f"  步長: 0.5°")
        print(f"  最佳角度: {best_angle:.2f}°")
        print(f"  最大方差: {max_variance:.0f}")
        print(f"  置信度: {confidence:.2%}")
    
    return best_angle, confidence


def detect_angle_by_lines(image: np.ndarray, verbose: bool = False) -> Tuple[float, float]:
    """
    使用霍夫線條變換檢測角度（改進版）
    
    Args:
        image: 輸入圖像
        verbose: 是否輸出詳細信息
    
    Returns:
        (angle, confidence): 角度和置信度
    """
    # 轉換為灰階
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # 邊緣檢測
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫線條變換
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                           minLineLength=100, maxLineGap=10)
    
    if lines is None or len(lines) == 0:
        return 0.0, 0.0
    
    # 計算每條線的角度
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        
        # 將角度標準化到 [-45, 45] 範圍
        if angle < -45:
            angle += 90
        elif angle > 45:
            angle -= 90
        
        angles.append(angle)
    
    # 使用中位數作為最終角度（比平均值更穩定）
    median_angle = np.median(angles)
    
    # 置信度基於角度的一致性
    angle_std = np.std(angles)
    confidence = max(0, 1.0 - angle_std / 45.0)  # 標準差越小，置信度越高
    
    if verbose:
        print(f"  檢測到線條: {len(lines)}")
        print(f"  角度中位數: {median_angle:.2f}°")
        print(f"  角度標準差: {angle_std:.2f}°")
        print(f"  置信度: {confidence:.2%}")
    
    return median_angle, confidence


def detect_angle_combined(image: np.ndarray, verbose: bool = False) -> Tuple[float, float]:
    """
    綜合多種方法的檢測結果
    
    Args:
        image: 輸入圖像
        verbose: 是否輸出詳細信息
    
    Returns:
        (angle, confidence): 角度和置信度
    """
    if verbose:
        print("\n=== 方法 1: 輪廓檢測 ===")
    angle1, conf1 = detect_angle_by_contours(image, verbose)
    
    if verbose:
        print("\n=== 方法 2: 投影法 ===")
    angle2, conf2 = detect_angle_by_projection(image, verbose)
    
    if verbose:
        print("\n=== 方法 3: 霍夫線條 ===")
    angle3, conf3 = detect_angle_by_lines(image, verbose)
    
    # 加權平均（根據置信度）
    total_conf = conf1 + conf2 + conf3
    if total_conf > 0:
        weighted_angle = (angle1 * conf1 + angle2 * conf2 + angle3 * conf3) / total_conf
        final_confidence = total_conf / 3.0  # 平均置信度
    else:
        weighted_angle = 0.0
        final_confidence = 0.0
    
    if verbose:
        print("\n=== 綜合結果 ===")
        print(f"  輪廓: {angle1:.2f}° (權重: {conf1:.2%})")
        print(f"  投影: {angle2:.2f}° (權重: {conf2:.2%})")
        print(f"  線條: {angle3:.2f}° (權重: {conf3:.2%})")
        print(f"  最終角度: {weighted_angle:.2f}°")
        print(f"  最終置信度: {final_confidence:.2%}")
    
    return weighted_angle, final_confidence


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    旋轉圖像
    
    Args:
        image: 輸入圖像
        angle: 旋轉角度（度）
    
    Returns:
        旋轉後的圖像
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # 獲取旋轉矩陣
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # 計算旋轉後的邊界
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    
    # 調整旋轉矩陣
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    
    # 執行旋轉
    rotated = cv2.warpAffine(image, M, (new_w, new_h), 
                            flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(255, 255, 255))
    
    return rotated


def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    圖像增強
    
    Args:
        image: 輸入圖像
    
    Returns:
        增強後的圖像
    """
    # 降噪
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    # 轉換到 LAB 色彩空間
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # 應用 CLAHE 到 L 通道
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # 合併通道
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # 銳化
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    return sharpened


def preprocess_image(image: np.ndarray, method: str = 'combined',
                    verbose: bool = False) -> Tuple[np.ndarray, float]:
    """
    預處理圖像
    
    Args:
        image: 輸入圖像
        method: 檢測方法 ('contours', 'projection', 'lines', 'combined')
        verbose: 是否輸出詳細信息
    
    Returns:
        (processed_image, angle): 處理後的圖像和旋轉角度
    """
    if verbose:
        print(f"\n=== OpenCV 進階角度檢測 ({method}) ===")
    
    # 檢測角度
    if method == 'contours':
        angle, confidence = detect_angle_by_contours(image, verbose)
    elif method == 'projection':
        angle, confidence = detect_angle_by_projection(image, verbose)
    elif method == 'lines':
        angle, confidence = detect_angle_by_lines(image, verbose)
    else:  # combined
        angle, confidence = detect_angle_combined(image, verbose)
    
    if verbose:
        print(f"\n=== 應用旋轉 ===")
        print(f"  旋轉角度: {angle:.2f}°")
        print(f"  置信度: {confidence:.2%}")
    
    # 旋轉圖像
    rotated = rotate_image(image, angle)
    
    if verbose:
        print("\n=== 圖像增強 ===")
        print("  應用降噪...")
        print("  增強對比度 (CLAHE)...")
        print("  應用銳化...")
    
    # 增強圖像
    enhanced = enhance_image(rotated)
    
    return enhanced, angle


def visualize_detection(image: np.ndarray, method: str, output_path: str):
    """
    視覺化檢測過程
    
    Args:
        image: 輸入圖像
        method: 檢測方法
        output_path: 輸出路徑
    """
    fig_image = image.copy()
    
    if method == 'contours':
        # 顯示輪廓
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cv2.drawContours(fig_image, contours, -1, (0, 255, 0), 2)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            rect = cv2.minAreaRect(largest)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(fig_image, [box], 0, (0, 0, 255), 3)
    
    elif method == 'lines':
        # 顯示檢測到的線條
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                               minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(fig_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    cv2.imwrite(output_path, fig_image)
    print(f"視覺化圖像已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='OpenCV 進階角度檢測工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', required=True, help='輸出圖像路徑')
    parser.add_argument('--method', '-m', 
                       choices=['contours', 'projection', 'lines', 'combined'],
                       default='combined',
                       help='檢測方法：contours（輪廓）、projection（投影）、lines（線條）、combined（綜合）')
    parser.add_argument('--visualize', '-v', help='保存視覺化結果的路徑')
    parser.add_argument('--verbose', action='store_true', help='顯示詳細信息')
    
    args = parser.parse_args()
    
    # 讀取圖像
    print(f"讀取圖像: {args.input}")
    image = cv2.imread(args.input)
    
    if image is None:
        print(f"錯誤: 無法讀取圖像 {args.input}")
        return
    
    print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 預處理圖像
    processed, rotation_angle = preprocess_image(image, args.method, args.verbose)
    
    # 保存結果
    cv2.imwrite(args.output, processed)
    print(f"\n處理完成！")
    print(f"旋轉角度: {rotation_angle:.2f}°")
    print(f"輸出檔案: {args.output}")
    
    # 視覺化（如果需要）
    if args.visualize:
        visualize_detection(image, args.method, args.visualize)


if __name__ == '__main__':
    main()
