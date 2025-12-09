#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Excel 解析器
"""

import os
import sys

# 取得 example.xlsx 路徑
example_file = "../6_Desktop_App/input/example.xlsx"

if not os.path.exists(example_file):
    print(f"找不到檔案: {example_file}")
    sys.exit(1)

# 執行解析
os.system(f"python3 excel_parser.py {example_file}")
