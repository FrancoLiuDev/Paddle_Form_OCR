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



def apply_angle_correction(image: np.ndarray, angle: float, verbose: bool = False) -> np.ndarray:
    """
    應用角度修正
    
    Args:
        image: 輸入圖像
        angle: 修正角度（度）
        verbose: 是否顯示詳細輸出
        
    Returns:
        修正後的圖像
    """
    if verbose:
        print(f"  應用角度修正: {angle:.2f}°")
    
    # 獲取圖像中心
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    # 創建旋轉矩陣
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # 應用旋轉
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                            flags=cv2.INTER_LINEAR, 
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(255, 255, 255))
    
    if verbose:
        print(f"  角度修正完成")
    
    return rotated


def detect_and_fill_text_regions(image: np.ndarray) -> np.ndarray:
    """
    檢測文字密集區域並填黑，以突顯文字走向
    
    Args:
        image: 輸入的灰階圖像
        
    Returns:
        填黑文字區域後的圖像
    """
    result = image.copy()
    
    # 1. 使用自適應閾值二值化來檢測文字
    binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # 2. 使用更小的形態學操作連接文字，避免過度填充
    # 水平方向的核心，用於連接文字行（進一步減小，讓文字行更細）
    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
    # 垂直方向的核心，用於連接文字列（保持原有尺寸）
    kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4))
    
    # 3. 較溫和的膨脹操作連接文字
    dilated_h = cv2.dilate(binary, kernel_horizontal, iterations=1)
    dilated_v = cv2.dilate(binary, kernel_vertical, iterations=1)
    
    # 4. 合併水平和垂直方向的結果
    combined = cv2.bitwise_or(dilated_h, dilated_v)
    
    # 5. 輕微膨脹以填滿文字區域（使用更細的核心讓文字行更細）
    kernel_fill = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 2))
    filled = cv2.dilate(combined, kernel_fill, iterations=1)
    
    # 6. 使用輪廓檢測找到文字區域
    contours, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 7. 進一步提高面積闾值，只保留真正的文字行
    min_area = 2000  # 適度降低闾值，保留文字行但保持細節
    text_mask = np.zeros_like(image)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            # 使用原始輪廓而不是凸包，避免過度填充
            cv2.fillPoly(text_mask, [contour], 255)
    
    # 8. 將文字區域填黑
    result[text_mask == 255] = 0
    
    return result


def preprocess_image_for_line_detection(gray_image: np.ndarray) -> np.ndarray:
    """
    專門為線條檢測優化的圖像預處理
    
    Args:
        gray_image: 輸入的灰階圖像
        
    Returns:
        處理後適合線條檢測的圖像
    """
    # 添加適度模糊處理以減少雜訊（減少模糊強度讓文字更精確）
    print("  應用適度模糊...")
    blurred = cv2.GaussianBlur(gray_image, (15, 15), 3.0)
    print(f"  模糊參數: kernel_size=(15,15), sigma=3.0 (適度模糊)")
    
    # 添加強化銳化處理以增強邊緣
    print("  應用強化銳化處理以增強邊緣...")
    kernel_sharpen = np.array([[-2, -2, -2],
                              [-2, 17, -2],
                              [-2, -2, -2]])
    sharpened = cv2.filter2D(blurred, -1, kernel_sharpen)
    
    # 再次應用更強的銳化
    kernel_sharpen2 = np.array([[-1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1],
                               [-1, -1, 25, -1, -1],
                               [-1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1]])
    sharpened = cv2.filter2D(sharpened, -1, kernel_sharpen2)
    print(f"  銳化核心: 3x3 強化核心 + 5x5 超強核心")
    
    # 文字密集區域檢測和填黑處理
    print("  檢測文字密集區域並填黑...")
    text_filled = detect_and_fill_text_regions(sharpened)
    print(f"  文字區域填黑完成")
    
    return text_filled




def detect_angle_by_lines(image: np.ndarray, output_path: str, degree_limit: Optional[float] = None, min_line_length: int = 50, skip_preprocessing: bool = False) -> np.ndarray:
    """
    可視化霍夫直線檢測結果，用紅色標記檢測到的線條
    並統計每條線與水平線的角度
    
    Args:
        image: 輸入圖像
        output_path: 輸出路徑
        degree_limit: 角度限制（例如 10 表示只顯示 ±10° 內的線條），None 表示顯示全部
        min_line_length: 最小線條長度（像素），用於過濾短線條
        skip_preprocessing: 是否跳過圖像預處理（當圖像已經預處理過時使用）
    """
    result = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    
    if skip_preprocessing:
        print("  跳過重複的圖像預處理，直接進行線條檢測...")
        # 直接使用輸入圖像進行線條檢測
        text_filled = gray
    else:
        # 使用專用的線條檢測預處理
        text_filled = preprocess_image_for_line_detection(gray)
        
    # 邊緣檢測（使用預處理後的圖像）
    edges = cv2.Canny(text_filled, 30, 100, apertureSize=3)
    print(f"  Canny 邊緣檢測參數: low_threshold=30, high_threshold=100 (高敏感度)")
        
    # 霍夫直線檢測（提高敏感度）
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=20)
    print(f"  霍夫變換參數: threshold=50, minLineLength=30, maxLineGap=20 (高敏感度)")
    
    # 初始化變數
    filtered_lines = []
    filtered_angles = []
    filtered_lengths = []
    most_common_angle = None
    
    if lines is not None:
        # 儲存所有角度和過濾後的線條
        all_angles = []
        candidate_lines = []  # 暫存符合條件的線條
        
        # 第一步：計算所有線條的角度和長度，過濾角度範圍
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)  # 計算線條長度
            all_angles.append(angle)
            
            # 判斷是否在角度範圍內且長度足夠
            if (degree_limit is None or abs(angle) <= degree_limit) and length >= min_line_length:
                candidate_lines.append({
                    'coords': line[0],
                    'angle': angle,
                    'length': length
                })
        
        # 第二步：按長度排序，只取最長的 20 條
        candidate_lines.sort(key=lambda x: x['length'], reverse=True)
        top_lines = candidate_lines[:20]  # 只取前 20 條最長的線
        
        # 提取最終使用的線條資訊
        filtered_lines = [line['coords'] for line in top_lines]
        filtered_angles = [line['angle'] for line in top_lines]
        filtered_lengths = [line['length'] for line in top_lines]
        
        print(f"  檢測到 {len(lines)} 條線")
        if degree_limit is not None:
            print(f"  符合角度範圍 (±{degree_limit}°) 的線: {len(candidate_lines)} 條")
        if min_line_length > 0:
            print(f"  符合長度限制 (≥{min_line_length}px) 的線: {len(candidate_lines)} 條")
        print(f"  使用最長的 {len(top_lines)} 條線進行角度計算")
        
        # 先計算最優角度，用於區分顏色
        most_common_angle = None
        if len(filtered_lines) > 0:
            angles_array = np.array(filtered_angles)
            lengths_array = np.array(filtered_lengths)
            
            # 使用長度加權計算最優角度（長線條權重更大）
            rounded_angles = np.round(angles_array, 1)
            angle_weights = {}
            for angle, length in zip(rounded_angles, lengths_array):
                if angle not in angle_weights:
                    angle_weights[angle] = 0
                angle_weights[angle] += length
            
            # 找出總長度最大的角度
            weighted_best_angle = max(angle_weights.items(), key=lambda x: x[1])[0]
            most_common_angle = weighted_best_angle
        
        # 繪製過濾後的線條（統一使用紅色）
        line_thickness = 8  # 增加線條粗細為更明顯
        for line_coords in filtered_lines:
            x1, y1, x2, y2 = line_coords
            
            # 所有線條都用紅色
            color = (0, 0, 255)  # 紅色
            
            cv2.line(result, (x1, y1), (x2, y2), color, line_thickness)
        
        # 顯示詳細信息
        if len(filtered_lines) > 0:
            print(f"\n  線條角度統計（與水平線的角度）:")
            print(f"  {'序號':<6} {'起點':<15} {'終點':<15} {'角度':<10}")
            print(f"  {'-'*50}")
            
            for idx, (line_coords, angle) in enumerate(zip(filtered_lines, filtered_angles), 1):
                x1, y1, x2, y2 = line_coords
                
                # 只顯示前 20 條詳細信息
                if idx <= 20:
                    print(f"  {idx:<6} ({x1:>3},{y1:>3}) -> ({x2:>3},{y2:>3})  {angle:>6.2f}°")
            
            if len(filtered_lines) > 20:
                print(f"  ... (省略剩餘 {len(filtered_lines)-20} 條線)")
            
            # 統計過濾後的角度分布
            angles_array = np.array(filtered_angles)
            lengths_array = np.array(filtered_lengths)
            
            # 方法1: 計算最多出現的角度（眾數，不考慮長度）
            rounded_angles = np.round(angles_array, 1)
            unique_angles, counts = np.unique(rounded_angles, return_counts=True)
            most_common_idx = np.argmax(counts)
            most_common_angle = unique_angles[most_common_idx]
            most_common_count = counts[most_common_idx]
            
            # 方法2: 使用長度加權計算最優角度（長線條權重更大）
            # 將角度分組（每0.1度一組），累加每組的總長度
            angle_weights = {}
            for angle, length in zip(rounded_angles, lengths_array):
                if angle not in angle_weights:
                    angle_weights[angle] = 0
                angle_weights[angle] += length
            
            # 找出總長度最大的角度
            weighted_best_angle = max(angle_weights.items(), key=lambda x: x[1])[0]
            weighted_total_length = angle_weights[weighted_best_angle]
            
            # 計算該角度的線條數量
            weighted_count = np.sum(rounded_angles == weighted_best_angle)
            
            print(f"\n  過濾後角度統計:")
            print(f"  {'最小角度:':<20} {np.min(angles_array):>6.2f}°")
            print(f"  {'最大角度:':<20} {np.max(angles_array):>6.2f}°")
            print(f"  {'平均角度:':<20} {np.mean(angles_array):>6.2f}°")
            print(f"  {'中位數角度:':<20} {np.median(angles_array):>6.2f}°")
            print(f"  {'最多出現的角度:':<20} {most_common_angle:>6.2f}° (出現 {most_common_count} 次)")
            print(f"  {'長度加權最優角度:':<20} {weighted_best_angle:>6.2f}° ({weighted_count} 條線，總長 {weighted_total_length:.0f}px)")
            print(f"  {'標準差:':<20} {np.std(angles_array):>6.2f}°")
            
            # 使用長度加權的角度作為最終輸出（已在繪製時計算）
            most_common_angle = weighted_best_angle
            
            # 統計線條數量
            print(f"  {'線條標記:':<20}")
            print(f"  {'  紅色線條:':<20} {len(filtered_lines)} 條 (全部)")
        else:
            if degree_limit is not None:
                print(f"\n  沒有符合角度範圍 (±{degree_limit}°) 的線條")
        
        # 顯示全部線條的統計
        if degree_limit is not None and len(all_angles) > 0:
            all_angles_array = np.array(all_angles)
            print(f"\n  全部線條角度統計（參考）:")
            print(f"  {'最小角度:':<15} {np.min(all_angles_array):>6.2f}°")
            print(f"  {'最大角度:':<15} {np.max(all_angles_array):>6.2f}°")
            print(f"  {'平均角度:':<15} {np.mean(all_angles_array):>6.2f}°")
        
    else:
        print("  未檢測到線條")
    
    # 可選：儲存可視化結果圖片（透過環境變數 SAVE_LINES_IMAGE=1 啟用）
    import os
    if output_path and os.environ.get('SAVE_LINES_IMAGE', '0') == '1':
        vis_path = output_path.replace('.', '_lines.')
        cv2.imwrite(vis_path, result)
        print(f"\n  線條可視化已儲存至: {vis_path}")
    
    # 返回結果和最常見的角度
    if len(filtered_lines) > 0:
        return result, most_common_angle
    else:
        return result, None



def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """旋轉圖像"""
    print(f"輸入角度: {angle}°")
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
        # arctan2: 負值=向左傾斜，正值=向右傾斜
        # getRotationMatrix2D: 正值=逆時針，負值=順時針
        # 修正: 直接使用 angle (檢測到-12°，轉-12°順時針修正)
        center = (w // 2, h // 2)
        print(f"getRotationMatrix2D: {angle}°")
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
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


def preprocess_image(image: np.ndarray, verbose: bool = False) -> np.ndarray:
    """
    完整的圖像預處理流程（不包含旋轉）
    
    返回:
        processed_image: 處理後的灰階圖像
    """

    # 1. 降噪
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
    
    # 保持灰階格式，不轉回彩色
    result = sharpened
    
    if verbose:
        print("\n預處理完成！")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='霍夫直線檢測預處理工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', required=True, help='輸出圖像路徑')
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
    
    # 預處理 - 總是使用專門的線條檢測預處理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    processed = preprocess_image_for_line_detection(gray)
    
    # 應用文字區域檢測和填黑處理
    processed_with_text_fill = detect_and_fill_text_regions(processed)
    
    # detect_angle_by_lines 
    rotation_angle, confidence = detect_angle_by_lines(processed_with_text_fill, verbose=args.verbose)
    if rotation_angle != 0:
        if args.verbose:
            print(f"旋轉角度: {rotation_angle}°，置信度: {confidence:.2f}")
        rotated_image = rotate_image(processed, rotation_angle)
    else:
        rotated_image = processed
     
    # 儲存結果
    cv2.imwrite(args.output, rotated_image)
    
    if args.verbose:
        print(f"\n處理完成！")
        print(f"輸出檔案: {args.output}")
    else:
        print(f"已儲存至: {args.output}")


if __name__ == '__main__':
    main()
