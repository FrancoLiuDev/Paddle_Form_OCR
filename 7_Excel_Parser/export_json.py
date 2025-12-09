#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 Excel 並輸出 JSON 結果到 result 目錄
"""

import os
import sys
import json
from datetime import datetime
from excel_parser import ExcelParser


def main():
    # 目標檔案
    example_file = "../6_Desktop_App/input/example.xlsx"
    
    if not os.path.exists(example_file):
        print(f"❌ 找不到檔案: {example_file}")
        sys.exit(1)
    
    print(f"📂 正在解析: {example_file}")
    
    # 執行解析
    parser = ExcelParser(example_file)
    result = parser.parse()
    
    if not result.get("success"):
        print(f"❌ 解析失敗: {result.get('error')}")
        sys.exit(1)
    
    # 確保 result 目錄存在
    result_dir = "result"
    os.makedirs(result_dir, exist_ok=True)
    
    # 輸出完整 JSON
    output_file = os.path.join(result_dir, "example_excel_full.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完整結果已輸出: {output_file}")
    print(f"   檔案大小: {os.path.getsize(output_file):,} bytes")
    
    # 輸出摘要 JSON（不包含詳細資料）
    summary_result = {
        "success": result["success"],
        "file_info": result["file_info"],
        "workbook_info": result["workbook_info"],
        "sheets_summary": []
    }
    
    for sheet in result["sheets"]:
        sheet_summary = {
            "name": sheet["name"],
            "range": sheet["range"],
            "headers": sheet["headers"],
            "statistics": sheet["statistics"],
            "merged_cells_count": len(sheet["merged_cells"]),
            "has_more": sheet["has_more"]
        }
        summary_result["sheets_summary"].append(sheet_summary)
    
    summary_file = os.path.join(result_dir, "example_excel_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 摘要結果已輸出: {summary_file}")
    print(f"   檔案大小: {os.path.getsize(summary_file):,} bytes")
    
    # 顯示基本資訊
    print(f"\n📊 分析摘要:")
    print(f"   工作表數量: {result['workbook_info']['total_sheets']}")
    print(f"   工作表名稱: {', '.join(result['workbook_info']['sheet_names'])}")
    
    total_cells = sum(s["statistics"]["total_cells"] for s in result["sheets"])
    total_filled = sum(s["statistics"]["total_cells"] - s["statistics"]["empty_cells"] for s in result["sheets"])
    
    print(f"   總儲存格數: {total_cells:,}")
    print(f"   已填充數: {total_filled:,}")
    print(f"   總填充率: {total_filled / total_cells * 100:.1f}%")
    
    print(f"\n✨ 完成！")


if __name__ == "__main__":
    main()
