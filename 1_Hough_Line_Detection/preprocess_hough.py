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


def visualize_line_detection(image: np.ndarray, output_path: str, degree_limit: Optional[float] = None) -> np.ndarray:
    """
    可視化霍夫直線檢測結果，用紅色標記檢測到的線條
    並統計每條線與水平線的角度
    
    Args:
        image: 輸入圖像
        output_path: 輸出路徑
        degree_limit: 角度限制（例如 10 表示只顯示 ±10° 內的線條），None 表示顯示全部
    """
    result = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    
    # 邊緣檢測
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # 霍夫直線檢測
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    
    if lines is not None:
        # 儲存所有角度和過濾後的線條
        all_angles = []
        filtered_lines = []
        filtered_angles = []
        
        # 計算所有線條的角度
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            all_angles.append(angle)
            
            # 判斷是否在角度範圍內
            if degree_limit is None or abs(angle) <= degree_limit:
                filtered_lines.append(line[0])
                filtered_angles.append(angle)
        
        print(f"  檢測到 {len(lines)} 條線")
        if degree_limit is not None:
            print(f"  符合角度範圍 (±{degree_limit}°) 的線: {len(filtered_lines)} 條")
        
        # 繪製過濾後的線條
        for line_coords in filtered_lines:
            x1, y1, x2, y2 = line_coords
            cv2.line(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
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
            
            # 計算最多出現的角度（眾數）
            # 將角度四捨五入到 0.1 度來統計
            rounded_angles = np.round(angles_array, 1)
            unique_angles, counts = np.unique(rounded_angles, return_counts=True)
            most_common_idx = np.argmax(counts)
            most_common_angle = unique_angles[most_common_idx]
            most_common_count = counts[most_common_idx]
            
            print(f"\n  過濾後角度統計:")
            print(f"  {'最小角度:':<20} {np.min(angles_array):>6.2f}°")
            print(f"  {'最大角度:':<20} {np.max(angles_array):>6.2f}°")
            print(f"  {'平均角度:':<20} {np.mean(angles_array):>6.2f}°")
            print(f"  {'中位數角度:':<20} {np.median(angles_array):>6.2f}°")
            print(f"  {'最多出現的角度:':<20} {most_common_angle:>6.2f}° (出現 {most_common_count} 次)")
            print(f"  {'標準差:':<20} {np.std(angles_array):>6.2f}°")
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
    
    # 儲存可視化結果
    if output_path:
        vis_path = output_path.replace('.', '_lines.')
        cv2.imwrite(vis_path, result)
        print(f"\n  線條可視化已儲存至: {vis_path}")
    
    # 返回結果和最常見的角度
    if len(filtered_lines) > 0:
        return result, most_common_angle
    else:
        return result, None


def detect_blank_separators(image: np.ndarray, angle: float, output_path: str = None, 
                           angle_tolerance: float = 5.0, 
                           scan_step: int = 5,
                           min_blank_length: int = 30,
                           white_threshold: int = 240) -> np.ndarray:
    """
    沿著指定角度方向掃描文件，找出連續的空白分隔線
    
    Args:
        image: 輸入圖像
        angle: 掃描方向的角度（與水平線的角度）
        output_path: 輸出路徑
        angle_tolerance: 角度容差（±度）
        scan_step: 掃描間隔（像素）
        min_blank_length: 最小連續空白長度（像素）
        white_threshold: 白色閾值（灰度值）
    
    Returns:
        標記了空白分隔線的圖像
    """
    print(f"\n=== 空白分隔線檢測 ===")
    print(f"  掃描角度: {angle:.2f}°")
    print(f"  掃描間隔: {scan_step} 像素")
    print(f"  最小空白長度: {min_blank_length} 像素")
    print(f"  白色閾值: {white_threshold}")
    
    result = image.copy()  # 用於繪製掃描線（紅色）+ 空白線（綠色）
    result_clean = image.copy()  # 用於只繪製空白線（綠色）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    h, w = gray.shape
    
    blank_regions = []
    
    # 如果角度接近水平（±10度），則沿垂直方向掃描（逐行）
    if abs(angle) <= 10 or abs(angle - 180) <= 10:
        print(f"  掃描方向: 垂直掃描（逐行檢查水平空白線）")
        
        # 先建立每一行的白色比例
        row_blank_map = []
        for y in range(h):
            row = gray[y, :]
            white_count = np.sum(row >= white_threshold)
            white_ratio = white_count / w
            row_blank_map.append(white_ratio)
        
        # 找出連續的空白行區域（白色比例 > 0.9）
        in_blank_region = False
        region_start = 0
        
        for y in range(h):
            is_blank = row_blank_map[y] > 0.9
            
            if is_blank and not in_blank_region:
                # 開始一個新的空白區域
                region_start = y
                in_blank_region = True
            elif not is_blank and in_blank_region:
                # 結束當前空白區域
                region_height = y - region_start
                if region_height >= 3:  # 至少3行高
                    # 檢查這個區域內是否有足夠長的水平空白線
                    region_middle = region_start + region_height // 2
                    row = gray[region_middle, :]
                    white_pixels = row >= white_threshold
                    
                    # 找連續的白色區段
                    start = None
                    for x in range(w):
                        if white_pixels[x]:
                            if start is None:
                                start = x
                        else:
                            if start is not None:
                                length = x - start
                                if length >= min_blank_length:
                                    blank_regions.append({
                                        'type': 'horizontal',
                                        'y': region_middle,
                                        'y_start': region_start,
                                        'y_end': y,
                                        'x_start': start,
                                        'x_end': x,
                                        'length': length
                                    })
                                start = None
                    
                    # 檢查最後一段
                    if start is not None:
                        length = w - start
                        if length >= min_blank_length:
                            blank_regions.append({
                                'type': 'horizontal',
                                'y': region_middle,
                                'y_start': region_start,
                                'y_end': y,
                                'x_start': start,
                                'x_end': w,
                                'length': length
                            })
                
                in_blank_region = False
    
    # 如果角度接近垂直（90度±10度），則沿水平方向掃描（逐列）
    elif abs(angle - 90) <= 10 or abs(angle + 90) <= 10:
        print(f"  掃描方向: 水平掃描（逐列檢查垂直空白線）")
        
        # 先建立每一列的白色比例
        col_blank_map = []
        for x in range(w):
            col = gray[:, x]
            white_count = np.sum(col >= white_threshold)
            white_ratio = white_count / h
            col_blank_map.append(white_ratio)
        
        # 找出連續的空白列區域（白色比例 > 0.9）
        in_blank_region = False
        region_start = 0
        
        for x in range(w):
            is_blank = col_blank_map[x] > 0.9
            
            if is_blank and not in_blank_region:
                # 開始一個新的空白區域
                region_start = x
                in_blank_region = True
            elif not is_blank and in_blank_region:
                # 結束當前空白區域
                region_width = x - region_start
                if region_width >= 3:  # 至少3列寬
                    # 檢查這個區域內是否有足夠長的垂直空白線
                    region_middle = region_start + region_width // 2
                    col = gray[:, region_middle]
                    white_pixels = col >= white_threshold
                    
                    # 找連續的白色區段
                    start = None
                    for y in range(h):
                        if white_pixels[y]:
                            if start is None:
                                start = y
                        else:
                            if start is not None:
                                length = y - start
                                if length >= min_blank_length:
                                    blank_regions.append({
                                        'type': 'vertical',
                                        'x': region_middle,
                                        'x_start': region_start,
                                        'x_end': x,
                                        'y_start': start,
                                        'y_end': y,
                                        'length': length
                                    })
                                start = None
                    
                    # 檢查最後一段
                    if start is not None:
                        length = h - start
                        if length >= min_blank_length:
                            blank_regions.append({
                                'type': 'vertical',
                                'x': region_middle,
                                'x_start': region_start,
                                'x_end': x,
                                'y_start': start,
                                'y_end': h,
                                'length': length
                            })
                
                in_blank_region = False
    else:
        # 對於其他角度，直接在原圖上沿角度方向掃描
        print(f"  掃描方向: 沿 {angle:.1f}° 角度直接掃描")
        
        # 計算掃描線的方向向量
        angle_rad = np.radians(angle)
        dx = np.cos(angle_rad)
        dy = np.sin(angle_rad)
        
        # 垂直於掃描線的方向（用於在垂直方向上移動掃描線）
        perp_dx = -dy
        perp_dy = dx
        
        # 計算需要掃描的範圍
        # 沿著垂直於線條的方向掃描
        diag = int(np.sqrt(w*w + h*h))  # 對角線長度
        
        # 從圖像中心開始，向兩側掃描
        center_x = w / 2
        center_y = h / 2
        
        scanned_lines = []
        row_white_ratios = []
        
        # 沿垂直方向掃描
        for offset in range(-diag, diag, scan_step):
            # 掃描線的中心點
            scan_center_x = center_x + offset * perp_dx
            scan_center_y = center_y + offset * perp_dy
            
            # 計算掃描線的起點和終點
            line_start_x = int(scan_center_x - diag * dx)
            line_start_y = int(scan_center_y - diag * dy)
            line_end_x = int(scan_center_x + diag * dx)
            line_end_y = int(scan_center_y + diag * dy)
            
            # 使用 Bresenham 算法獲取掃描線上的像素
            points = []
            x0, y0 = line_start_x, line_start_y
            x1, y1 = line_end_x, line_end_y
            
            # Bresenham's line algorithm
            dx_line = abs(x1 - x0)
            dy_line = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx_line - dy_line
            
            x, y = x0, y0
            while True:
                if 0 <= x < w and 0 <= y < h:
                    points.append((x, y))
                
                if x == x1 and y == y1:
                    break
                    
                e2 = 2 * err
                if e2 > -dy_line:
                    err -= dy_line
                    x += sx
                if e2 < dx_line:
                    err += dx_line
                    y += sy
            
            if len(points) > 0:
                # 記錄掃描線用於繪製
                if len(points) >= 2:
                    start_pt = points[0]
                    end_pt = points[-1]
                    scanned_lines.append({
                        'x1': start_pt[0], 'y1': start_pt[1],
                        'x2': end_pt[0], 'y2': end_pt[1],
                        'offset': offset,
                        'points': points  # 保存所有像素點
                    })
        
        print(f"  完成 {len(scanned_lines)} 條掃描線")
        
        # 在每條掃描線上找連續的空白區段
        print(f"  在每條掃描線上尋找連續空白區段...")
        print(f"  白色閾值: {white_threshold}")
        
        # 計算整體灰度統計
        overall_mean = np.mean(gray)
        overall_std = np.std(gray)
        print(f"  圖片灰度: 平均={overall_mean:.1f}, 標準差={overall_std:.1f}")
        
        # 如果圖片整體很白且對比度低，使用相對檢測
        use_relative = (overall_mean > 240 and overall_std < 30)
        if use_relative:
            print(f"  使用相對空白檢測模式（尋找比掃描線平均值更白的區域）")
        
        for scan_line in scanned_lines:
            points = scan_line['points']
            if len(points) < min_blank_length:
                continue
            
            # 獲取這條掃描線上的所有像素值
            pixel_values = [gray[y, x] for x, y in points]
            line_mean = np.mean(pixel_values)
            
            if use_relative:
                # 相對模式：找比這條線平均值更白的區域
                # 使用動態閾值：線平均值 + (255 - 線平均值) * 0.5
                dynamic_threshold = line_mean + (255 - line_mean) * 0.3
                is_white = [val >= dynamic_threshold for val in pixel_values]
            else:
                # 絕對模式：使用固定閾值
                is_white = [val >= white_threshold for val in pixel_values]
            
            # 計算這條線上的平均白度
            pixel_values = [gray[y, x] for x, y in points]
            line_avg = np.mean(pixel_values)
            
            # 找連續的白色區段
            blank_start = None
            for i, white in enumerate(is_white):
                if white and blank_start is None:
                    blank_start = i
                elif not white and blank_start is not None:
                    # 結束一個空白區段
                    blank_length = i - blank_start
                    if blank_length >= min_blank_length:
                        start_pt = points[blank_start]
                        end_pt = points[i-1]
                        segment_length = int(np.sqrt((end_pt[0]-start_pt[0])**2 + 
                                                     (end_pt[1]-start_pt[1])**2))
                        
                        blank_regions.append({
                            'type': 'angled',
                            'angle': angle,
                            'x1': start_pt[0],
                            'y1': start_pt[1],
                            'x2': end_pt[0],
                            'y2': end_pt[1],
                            'length': segment_length
                        })
                    blank_start = None
            
            # 檢查最後一段
            if blank_start is not None:
                blank_length = len(is_white) - blank_start
                if blank_length >= min_blank_length:
                    start_pt = points[blank_start]
                    end_pt = points[-1]
                    segment_length = int(np.sqrt((end_pt[0]-start_pt[0])**2 + 
                                                 (end_pt[1]-start_pt[1])**2))
                    
                    blank_regions.append({
                        'type': 'angled',
                        'angle': angle,
                        'x1': start_pt[0],
                        'y1': start_pt[1],
                        'x2': end_pt[0],
                        'y2': end_pt[1],
                        'length': segment_length
                    })
        
        print(f"  找到 {len(blank_regions)} 個空白區段")
        
        # 調試：統計空白區段的 Y 坐標分布
        if len(blank_regions) > 0:
            y_coords = []
            for blank in blank_regions:
                y_coords.append(blank['y1'])
                y_coords.append(blank['y2'])
            y_coords = np.array(y_coords)
            print(f"  空白區段 Y 坐標範圍: {y_coords.min()} - {y_coords.max()}")
            print(f"  Y > 300 的區段數: {np.sum(y_coords > 300)}/{len(y_coords)}")
        
        # 先建立只有綠線的版本
        result_clean = image.copy()
        
        # 繪製掃描過的線（紅色）- 在原圖上
        print(f"  繪製 {len(scanned_lines)} 條掃描線（紅色標記）")
        for scan_line in scanned_lines:
            cv2.line(result, 
                    (scan_line['x1'], scan_line['y1']), 
                    (scan_line['x2'], scan_line['y2']), 
                    (0, 0, 255), 2)  # 紅色，粗線（改為2像素）
    
    # 繪製檢測到的空白線
    print(f"\n  檢測到 {len(blank_regions)} 個空白分隔區域")
    
    # 繪製所有空白區域
    for idx, blank in enumerate(blank_regions, 1):
        if blank['type'] == 'horizontal':
            # 水平空白線用綠色標記（在兩個版本上都畫）
            cv2.line(result, 
                    (blank['x_start'], blank['y']), 
                    (blank['x_end'], blank['y']), 
                    (0, 255, 0), 2)
            cv2.line(result_clean, 
                    (blank['x_start'], blank['y']), 
                    (blank['x_end'], blank['y']), 
                    (0, 255, 0), 2)
            print(f"  {idx}. 水平空白區 at y={blank['y']} (範圍:{blank['y_start']}-{blank['y_end']}), x=[{blank['x_start']}-{blank['x_end']}], 長度={blank['length']}px")
        elif blank['type'] == 'vertical':
            # 垂直空白線用綠色標記
            cv2.line(result, 
                    (blank['x'], blank['y_start']), 
                    (blank['x'], blank['y_end']), 
                    (0, 255, 0), 2)
            cv2.line(result_clean, 
                    (blank['x'], blank['y_start']), 
                    (blank['x'], blank['y_end']), 
                    (0, 255, 0), 2)
            print(f"  {idx}. 垂直空白區 at x={blank['x']} (範圍:{blank['x_start']}-{blank['x_end']}), y=[{blank['y_start']}-{blank['y_end']}], 長度={blank['length']}px")
        elif blank['type'] == 'angled':
            # 傾斜空白線用綠色標記
            cv2.line(result, 
                    (blank['x1'], blank['y1']), 
                    (blank['x2'], blank['y2']), 
                    (0, 255, 0), 2)
            cv2.line(result_clean, 
                    (blank['x1'], blank['y1']), 
                    (blank['x2'], blank['y2']), 
                    (0, 255, 0), 2)
            if idx <= 20:  # 只打印前20條
                print(f"  {idx}. 傾斜空白區 ({blank['angle']:.1f}°) from ({blank['x1']},{blank['y1']}) to ({blank['x2']},{blank['y2']}), 長度={blank['length']}px")
    
    if len(blank_regions) > 20:
        print(f"  ... (省略剩餘 {len(blank_regions)-20} 個的打印輸出)")
    
    # 儲存兩個版本的結果
    if output_path:
        # 版本1: 只有綠色空白線
        blank_path_clean = output_path.replace('.', '_blanks.')
        cv2.imwrite(blank_path_clean, result_clean)
        print(f"\n  空白分隔線（純淨版）已儲存至: {blank_path_clean}")
        
        # 版本2: 紅色掃描線 + 綠色空白線
        blank_path_full = output_path.replace('.', '_blanks_with_scans.')
        cv2.imwrite(blank_path_full, result)
        print(f"  空白分隔線（含掃描線）已儲存至: {blank_path_full}")
    
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
    parser.add_argument('--degree', type=float, help='限定畫出紅線的角度範圍（例如：--degree 10 只畫出 ±10° 內的線條）')
    parser.add_argument('--detect-blanks', action='store_true', help='檢測空白分隔線（綠色標記）')
    parser.add_argument('--scan-step', type=int, default=5, help='空白掃描間隔（像素，預設：5）')
    parser.add_argument('--min-blank', type=int, default=30, help='最小空白長度（像素，預設：30）')
    parser.add_argument('--white-threshold', type=int, default=240, help='白色閾值（0-255，預設：240）')
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
        if args.degree is not None:
            print(f"  角度過濾: ±{args.degree}°")
        result, most_common_angle = visualize_line_detection(image, args.output, degree_limit=args.degree)
        
        # 如果啟用空白檢測
        if args.detect_blanks and most_common_angle is not None:
            print(f"\n使用最常見角度 {most_common_angle:.2f}° 進行空白檢測...")
            detect_blank_separators(
                image, 
                most_common_angle, 
                args.output,
                angle_tolerance=5.0,
                scan_step=args.scan_step,
                min_blank_length=args.min_blank,
                white_threshold=args.white_threshold
            )
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
        print(f"輸出檔案: {args.output}")
    else:
        print(f"已儲存至: {args.output}")


if __name__ == '__main__':
    main()
