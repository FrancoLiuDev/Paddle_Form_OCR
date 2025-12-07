#!/usr/bin/env python3
"""
全角度掃描工具
使用 Bresenham 演算法對圖像進行全角度掃描，找出空白率最高的最佳角度
"""

import cv2
import numpy as np
import argparse
from typing import List, Tuple, Dict
import sys


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """
    Bresenham 直線演算法，生成從 (x0,y0) 到 (x1,y1) 的所有點
    """
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    
    return points


def scan_at_angle(image: np.ndarray, angle: float, scan_step: int = 1, 
                  white_threshold: int = 199, min_blank_length: int = 30) -> Dict:
    """
    沿指定角度掃描圖像，計算空白率
    
    Args:
        image: 輸入圖像
        angle: 掃描角度（度）
        scan_step: 掃描間隔
        white_threshold: 白色閾值
        min_blank_length: 最小連續空白長度（未使用，保留參數相容性）
    
    Returns:
        包含統計數據的字典
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    h, w = gray.shape
    
    # 計算掃描線的起點和終點
    angle_rad = np.radians(angle)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # 計算垂直於掃描方向的方向向量
    perp_angle = angle + 90
    perp_rad = np.radians(perp_angle)
    perp_cos = np.cos(perp_rad)
    perp_sin = np.sin(perp_rad)
    
    # 確定掃描範圍
    diagonal = int(np.sqrt(w*w + h*h))
    center_x, center_y = w // 2, h // 2
    
    scan_lines = []
    total_white_pixels = 0
    total_scanned_pixels = 0
    blank_lines = 0
    
    # 沿垂直方向掃描
    for offset in range(-diagonal, diagonal, scan_step):
        # 計算掃描線的中心點
        mid_x = center_x + offset * perp_cos
        mid_y = center_y + offset * perp_sin
        
        # 計算掃描線的起點和終點
        x1 = int(mid_x - diagonal * cos_a)
        y1 = int(mid_y - diagonal * sin_a)
        x2 = int(mid_x + diagonal * cos_a)
        y2 = int(mid_y + diagonal * sin_a)
        
        # 使用 Bresenham 演算法生成掃描線上的點
        points = bresenham_line(x1, y1, x2, y2)
        
        # 過濾出在圖像範圍內的點
        valid_points = [(x, y) for x, y in points if 0 <= x < w and 0 <= y < h]
        
        if len(valid_points) == 0:
            continue
        
        # 計算這條掃描線上的白色像素數和最小像素值
        pixel_values = [gray[y, x] for x, y in valid_points]
        white_count = sum(1 for pv in pixel_values if pv >= white_threshold)
        min_pixel = min(pixel_values)
        
        total_scanned_pixels += len(valid_points)
        total_white_pixels += white_count
        
        # 判斷是否為空白線：整條線上所有像素都 >= 220（沒有黑點）
        if min_pixel >= 220:
            blank_lines += 1
        
        scan_lines.append({
            'offset': offset,
            'points': len(valid_points),
            'white_pixels': white_count,
            'white_rate': white_count / len(valid_points) if len(valid_points) > 0 else 0
        })
    
    # 計算統計數據
    blank_rate = (blank_lines / len(scan_lines) * 100) if len(scan_lines) > 0 else 0
    white_pixel_rate = (total_white_pixels / total_scanned_pixels * 100) if total_scanned_pixels > 0 else 0
    
    return {
        'angle': angle,
        'scan_lines': len(scan_lines),
        'blank_lines': blank_lines,
        'blank_rate': blank_rate,
        'total_pixels': total_scanned_pixels,
        'white_pixels': total_white_pixels,
        'white_pixel_rate': white_pixel_rate
    }


def full_angle_scan(image: np.ndarray, angle_start: float = -90, angle_end: float = 90,
                    angle_step: float = 1.0, scan_step: int = 1, 
                    white_threshold: int = 199, min_blank_length: int = 30,
                    verbose: bool = False) -> List[Dict]:
    """
    全角度掃描，測試所有角度並找出最佳角度
    
    Args:
        image: 輸入圖像
        angle_start: 起始角度
        angle_end: 結束角度
        angle_step: 角度步進
        scan_step: 掃描間隔
        white_threshold: 白色閾值
        min_blank_length: 最小連續空白長度
        verbose: 是否顯示詳細信息
    
    Returns:
        所有角度的統計數據列表
    """
    print(f"\n{'='*70}")
    print(f"全角度掃描測試")
    print(f"{'='*70}")
    print(f"角度範圍: {angle_start}° 到 {angle_end}°")
    print(f"角度步進: {angle_step}°")
    print(f"掃描間隔: {scan_step} 像素")
    print(f"白色閾值: {white_threshold}")
    print(f"最小空白長度: {min_blank_length} 像素")
    print(f"總共測試角度數: {int((angle_end - angle_start) / angle_step) + 1}")
    print(f"{'='*70}\n")
    
    results = []
    angle = angle_start
    count = 0
    total_angles = int((angle_end - angle_start) / angle_step) + 1
    
    while angle <= angle_end:
        count += 1
        if verbose or count % 10 == 0:
            print(f"測試角度 {angle:6.1f}° ({count}/{total_angles})...", end='\r')
        
        stats = scan_at_angle(image, angle, scan_step, white_threshold, min_blank_length)
        results.append(stats)
        
        angle += angle_step
    
    print(f"\n{'='*70}")
    print(f"掃描完成！")
    print(f"{'='*70}\n")
    
    return results


def display_results(results: List[Dict], top_n: int = 10):
    """
    顯示掃描結果
    
    Args:
        results: 統計數據列表
        top_n: 顯示前 N 個最佳角度
    """
    # 按空白率排序
    sorted_results = sorted(results, key=lambda x: x['blank_rate'], reverse=True)
    
    print(f"{'='*80}")
    print(f"前 {top_n} 個最佳角度（按空白率排序）")
    print(f"{'='*80}")
    print(f"{'排名':<6}{'角度':<10}{'掃描線':<10}{'空白線':<10}{'空白率':<12}{'白色點率'}")
    print(f"{'-'*80}")
    
    for i, stats in enumerate(sorted_results[:top_n], 1):
        marker = ' ✅' if i == 1 else ''
        print(f"{i:<6}{stats['angle']:6.1f}°{marker}  "
              f"{stats['scan_lines']:<10,}{stats['blank_lines']:<10,}"
              f"{stats['blank_rate']:>6.2f}%      {stats['white_pixel_rate']:>6.2f}%")
    
    best = sorted_results[0]
    print(f"\n最佳角度: {best['angle']:.1f}° (空白率 {best['blank_rate']:.2f}%)")
    print(f"{'='*80}\n")
    
    return sorted_results[0]


def visualize_best_angle(image: np.ndarray, angle: float, output_path: str,
                         scan_step: int = 1, white_threshold: int = 199,
                         min_blank_length: int = 30):
    """
    可視化最佳角度的掃描結果
    
    Args:
        image: 輸入圖像
        angle: 最佳角度
        output_path: 輸出路徑
        scan_step: 掃描間隔
        white_threshold: 白色閾值
        min_blank_length: 最小連續空白長度（未使用，保留參數相容性）
    """
    print(f"\n正在生成最佳角度 {angle:.1f}° 的可視化圖像...")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    result_with_scans = image.copy()  # 紅色掃描線 + 綠色空白線
    result_clean = image.copy()  # 只有綠色空白線
    h, w = gray.shape
    
    angle_rad = np.radians(angle)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    perp_angle = angle + 90
    perp_rad = np.radians(perp_angle)
    perp_cos = np.cos(perp_rad)
    perp_sin = np.sin(perp_rad)
    
    diagonal = int(np.sqrt(w*w + h*h))
    center_x, center_y = w // 2, h // 2
    
    blank_count = 0
    scan_count = 0
    
    for offset in range(-diagonal, diagonal, scan_step):
        mid_x = center_x + offset * perp_cos
        mid_y = center_y + offset * perp_sin
        
        x1 = int(mid_x - diagonal * cos_a)
        y1 = int(mid_y - diagonal * sin_a)
        x2 = int(mid_x + diagonal * cos_a)
        y2 = int(mid_y + diagonal * sin_a)
        
        points = bresenham_line(x1, y1, x2, y2)
        valid_points = [(x, y) for x, y in points if 0 <= x < w and 0 <= y < h]
        
        if len(valid_points) == 0:
            continue
        
        scan_count += 1
        
        # 計算最小像素值，判斷是否為空白線
        pixel_values = [gray[y, x] for x, y in valid_points]
        min_pixel = min(pixel_values)
        is_blank = (min_pixel >= 220)
        
        # 找到線段的實際起點和終點
        start_x, start_y = valid_points[0]
        end_x, end_y = valid_points[-1]
        
        # 所有掃描線用紅色標記（只在完整版上）
        cv2.line(result_with_scans, (start_x, start_y), (end_x, end_y), (0, 0, 255), 1)
        
        # 如果是空白線，用綠色標記（在兩個版本上都畫）
        if is_blank:
            blank_count += 1
            cv2.line(result_with_scans, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            cv2.line(result_clean, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
    
    # 儲存兩個版本
    # 版本1: 只有綠色空白線
    clean_path = output_path.replace('.', '_blanks.')
    cv2.imwrite(clean_path, result_clean)
    print(f"  空白線（純淨版）已儲存至: {clean_path}")
    
    # 版本2: 紅色掃描線 + 綠色空白線
    full_path = output_path.replace('.', '_blanks_with_scans.')
    cv2.imwrite(full_path, result_with_scans)
    print(f"  空白線（含掃描線）已儲存至: {full_path}")
    
    print(f"  統計: {scan_count} 條掃描線，{blank_count} 條空白線 ({blank_count/scan_count*100:.2f}%)")


def main():
    parser = argparse.ArgumentParser(description='全角度掃描工具')
    parser.add_argument('--input', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', default='best_angle.jpg', help='輸出圖像路徑')
    parser.add_argument('--angle-start', type=float, default=-90, help='起始角度（預設: -90）')
    parser.add_argument('--angle-end', type=float, default=90, help='結束角度（預設: 90）')
    parser.add_argument('--angle-step', type=float, default=1.0, help='角度步進（預設: 1.0）')
    parser.add_argument('--scan-step', type=int, default=5, help='掃描間隔（預設: 5）')
    parser.add_argument('--white-threshold', type=int, default=199, help='白色閾值（預設: 199）')
    parser.add_argument('--min-blank', type=int, default=30, help='最小連續空白長度（預設: 30）')
    parser.add_argument('--top-n', type=int, default=10, help='顯示前 N 個最佳角度（預設: 10）')
    parser.add_argument('--verbose', action='store_true', help='顯示詳細信息')
    parser.add_argument('--visualize', action='store_true', help='生成最佳角度的可視化圖像')
    
    args = parser.parse_args()
    
    # 讀取圖像
    image = cv2.imread(args.input)
    if image is None:
        print(f"錯誤: 無法讀取圖像 {args.input}")
        sys.exit(1)
    
    print(f"讀取圖像: {args.input}")
    print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 執行全角度掃描
    results = full_angle_scan(
        image,
        angle_start=args.angle_start,
        angle_end=args.angle_end,
        angle_step=args.angle_step,
        scan_step=args.scan_step,
        white_threshold=args.white_threshold,
        min_blank_length=args.min_blank,
        verbose=args.verbose
    )
    
    # 顯示結果
    best_result = display_results(results, top_n=args.top_n)
    
    # 如果需要，生成可視化圖像
    if args.visualize:
        visualize_best_angle(
            image,
            best_result['angle'],
            args.output,
            scan_step=args.scan_step,
            white_threshold=args.white_threshold,
            min_blank_length=args.min_blank
        )


if __name__ == '__main__':
    main()
