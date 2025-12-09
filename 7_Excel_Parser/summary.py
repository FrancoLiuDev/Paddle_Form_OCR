#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 摘要分析
只顯示關鍵資訊，不顯示詳細資料
"""

import sys
import json
from excel_parser import ExcelParser


def print_summary(result):
    """列印摘要資訊"""
    if not result.get("success"):
        print(f"❌ 解析失敗: {result.get('error')}")
        return
    
    print("=" * 60)
    print("📊 Excel 檔案分析摘要")
    print("=" * 60)
    
    # 檔案資訊
    file_info = result["file_info"]
    print(f"\n📁 檔案資訊:")
    print(f"   名稱: {file_info['name']}")
    print(f"   大小: {file_info['size_formatted']}")
    print(f"   修改時間: {file_info['modified']}")
    
    # 工作簿資訊
    wb_info = result["workbook_info"]
    print(f"\n📚 工作簿資訊:")
    print(f"   工作表數量: {wb_info['total_sheets']}")
    print(f"   工作表名稱: {', '.join(wb_info['sheet_names'])}")
    print(f"   目前作用中: {wb_info['active_sheet']}")
    
    # 各工作表詳細資訊
    for i, sheet in enumerate(result["sheets"], 1):
        print(f"\n{'─' * 60}")
        print(f"📄 工作表 {i}: {sheet['name']}")
        print(f"{'─' * 60}")
        
        # 範圍
        r = sheet["range"]
        print(f"   範圍: {r['total_rows']} 行 × {r['total_columns']} 列")
        print(f"   位置: R{r['min_row']}C{r['min_column']} ~ R{r['max_row']}C{r['max_column']}")
        
        # 標題
        if sheet["headers"]:
            print(f"\n   標題列: {', '.join(sheet['headers'][:5])}" + 
                  ("..." if len(sheet["headers"]) > 5 else ""))
        
        # 統計
        stats = sheet["statistics"]
        print(f"\n   📊 統計:")
        print(f"      總儲存格數: {stats['total_cells']}")
        print(f"      空白儲存格: {stats['empty_cells']} ({100 - stats['fill_rate']:.1f}%)")
        print(f"      數值儲存格: {stats['numeric_cells']}")
        print(f"      文字儲存格: {stats['text_cells']}")
        print(f"      日期儲存格: {stats['date_cells']}")
        print(f"      公式儲存格: {stats['formula_cells']}")
        print(f"      資料填充率: {stats['fill_rate']:.1f}%")
        
        # 數值統計
        if stats.get("numeric_stats"):
            ns = stats["numeric_stats"]
            print(f"\n   🔢 數值統計:")
            print(f"      數量: {ns['count']}")
            print(f"      總和: {ns['sum']:,.2f}")
            print(f"      平均: {ns['average']:,.2f}")
            print(f"      最小: {ns['min']:,.2f}")
            print(f"      最大: {ns['max']:,.2f}")
        
        # 合併儲存格
        if sheet["merged_cells"]:
            print(f"\n   🔗 合併儲存格: {len(sheet['merged_cells'])} 個")
            print(f"      範圍: {', '.join(sheet['merged_cells'][:3])}" +
                  ("..." if len(sheet["merged_cells"]) > 3 else ""))
    
    print(f"\n{'=' * 60}")
    print("✅ 分析完成")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 summary.py <excel_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    parser = ExcelParser(file_path)
    result = parser.parse()
    print_summary(result)


if __name__ == "__main__":
    main()
