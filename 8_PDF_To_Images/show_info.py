#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看轉換結果的統計資訊
"""

import os
from pathlib import Path
from PIL import Image


def analyze_images(image_dir: str):
    """分析圖片目錄的統計資訊
    
    Args:
        image_dir: 圖片目錄路徑
    """
    image_dir = Path(image_dir)
    
    if not image_dir.exists():
        print(f"❌ 目錄不存在: {image_dir}")
        return
    
    # 尋找圖片檔案
    image_files = sorted(list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg")))
    
    if not image_files:
        print(f"❌ 目錄中沒有圖片: {image_dir}")
        return
    
    print(f"\n📊 圖片統計分析")
    print(f"{'='*60}")
    print(f"目錄: {image_dir}")
    print(f"圖片數量: {len(image_files)}")
    print(f"{'='*60}\n")
    
    total_size = 0
    resolutions = []
    
    for i, img_file in enumerate(image_files, 1):
        # 檔案大小
        file_size = img_file.stat().st_size
        total_size += file_size
        
        # 圖片解析度
        try:
            with Image.open(img_file) as img:
                width, height = img.size
                mode = img.mode
                dpi = img.info.get('dpi', (0, 0))
                resolutions.append((width, height))
                
                print(f"📄 {i:2d}. {img_file.name}")
                print(f"     尺寸: {width} × {height} px")
                print(f"     檔案: {file_size / 1024:.1f} KB")
                print(f"     模式: {mode}")
                if dpi != (0, 0):
                    print(f"     DPI:  {dpi[0]:.0f}")
                print()
        except Exception as e:
            print(f"❌ 無法讀取 {img_file.name}: {e}\n")
    
    # 總計
    print(f"{'='*60}")
    print(f"📈 總計統計")
    print(f"{'='*60}")
    print(f"總圖片數: {len(image_files)}")
    print(f"總大小:   {total_size / 1024 / 1024:.2f} MB")
    print(f"平均大小: {total_size / len(image_files) / 1024:.1f} KB")
    
    if resolutions:
        avg_width = sum(r[0] for r in resolutions) / len(resolutions)
        avg_height = sum(r[1] for r in resolutions) / len(resolutions)
        print(f"平均尺寸: {avg_width:.0f} × {avg_height:.0f} px")
        
        # 計算實際 DPI (假設 A4 紙張: 210mm × 297mm)
        a4_width_inch = 210 / 25.4  # 8.27 英吋
        a4_height_inch = 297 / 25.4  # 11.69 英吋
        estimated_dpi = avg_width / a4_width_inch
        print(f"預估 DPI: {estimated_dpi:.0f} (基於 A4 尺寸)")
    
    print(f"{'='*60}\n")


def main():
    """主程式"""
    import sys
    
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # 預設分析最新的輸出目錄
        output_dir = Path("output")
        if not output_dir.exists():
            print("❌ 找不到 output 目錄")
            print("用法: python show_info.py <圖片目錄>")
            return
        
        subdirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], 
                        key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not subdirs:
            print("❌ output 目錄中沒有子目錄")
            return
        
        target_dir = subdirs[0]
    
    analyze_images(target_dir)


if __name__ == "__main__":
    main()
