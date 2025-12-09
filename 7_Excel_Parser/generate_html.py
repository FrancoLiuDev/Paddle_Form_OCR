#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將門市請款明細表 JSON 轉換為 HTML 表格
"""

import json
import os
from datetime import datetime


def generate_html(json_file: str, output_file: str):
    """生成 HTML 報表
    
    Args:
        json_file: JSON 檔案路徑
        output_file: 輸出 HTML 檔案路徑
    """
    # 讀取 JSON 資料
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data.get("success"):
        print(f"❌ JSON 資料無效: {data.get('error')}")
        return
    
    # 生成 HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>門市請款明細表</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft JhengHei', 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px 30px;
            border-radius: 8px;
            margin: 5px;
        }}
        
        .stat-item .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .stat-item .value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .controls {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .search-box {{
            width: 100%;
            max-width: 500px;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #667eea;
            border-radius: 25px;
            outline: none;
            transition: all 0.3s;
        }}
        
        .search-box:focus {{
            box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
        }}
        
        .store-section {{
            margin: 20px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s;
        }}
        
        .store-section:hover {{
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .store-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        
        .store-header:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
        }}
        
        .store-title {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .store-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .store-content {{
            display: none;
            padding: 0;
        }}
        
        .store-content.active {{
            display: block;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        thead {{
            background: #f8f9fa;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        th {{
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            font-size: 0.9em;
            white-space: nowrap;
        }}
        
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #f1f3f5;
            font-size: 0.85em;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .number {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
        
        .center {{
            text-align: center;
        }}
        
        .footer {{
            padding: 20px;
            text-align: center;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .expand-all {{
            padding: 10px 20px;
            margin-left: 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .expand-all:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .controls, .expand-all {{
                display: none;
            }}
            
            .store-content {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 門市請款明細表</h1>
            <div class="stats">
                <div class="stat-item">
                    <div class="label">總門市數</div>
                    <div class="value">{data['total_stores']}</div>
                </div>
                <div class="stat-item">
                    <div class="label">總資料行數</div>
                    <div class="value">{data['total_rows']:,}</div>
                </div>
                <div class="stat-item">
                    <div class="label">生成時間</div>
                    <div class="value" style="font-size: 1.2em;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="🔍 搜尋門市編碼或門市名稱...">
            <button class="expand-all" onclick="toggleAll()">展開/收合全部</button>
        </div>
        
        <div id="storesContainer">
"""
    
    # 生成每個門市的表格
    for store in data['stores']:
        store_code = store['門市編碼']
        store_name = store.get('門市名稱', '')
        items = store['項次列表']
        
        # 如果有項次資料，取得所有欄位名稱
        all_fields = []
        if items:
            all_fields = list(items[0].keys())
        
        html_content += f"""
            <div class="store-section" data-store-code="{store_code}" data-store-name="{store_name}">
                <div class="store-header" onclick="toggleStore(this)">
                    <div class="store-title">
                        🏪 門市編碼: {store_code} - {store_name}
                    </div>
                    <div class="store-badge">{len(items)} 筆設備</div>
                </div>
                <div class="store-content">
                    <table>
                        <thead>
                            <tr>
"""
        
        # 動態生成表頭
        for field in all_fields:
            align_class = "number" if any(keyword in field for keyword in ['金額', '數量', '單價', '費用', '列印量', '頁數']) else "center" if field == '項次' else ""
            html_content += f'                                <th class="{align_class}">{field}</th>\n'
        
        html_content += """
                            </tr>
                        </thead>
                        <tbody>
"""
        
        # 添加每個項次的資料
        for item in items:
            html_content += "                            <tr>\n"
            
            for field in all_fields:
                value = item.get(field, '')
                
                # 格式化值
                if value is None or value == 'None':
                    value_str = ''
                elif isinstance(value, (int, float)):
                    # 數字格式化
                    if any(keyword in field for keyword in ['金額', '單價', '費用']):
                        value_str = f'{float(value):,.4f}' if value != 0 else ''
                    elif any(keyword in field for keyword in ['數量', '列印量', '頁數']):
                        value_str = f'{int(value):,}' if isinstance(value, int) else f'{float(value):,.2f}'
                    else:
                        value_str = str(value)
                elif '日期' in field:
                    # 日期格式化
                    try:
                        value_str = str(value).split()[0] if value else ''
                    except:
                        value_str = str(value)
                else:
                    value_str = str(value)
                
                # 設定對齊方式
                align_class = "number" if any(keyword in field for keyword in ['金額', '數量', '單價', '費用', '列印量', '頁數']) else "center" if field == '項次' else ""
                
                html_content += f'                                <td class="{align_class}">{value_str}</td>\n'
            
            html_content += "                            </tr>\n"
        
        html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
"""
    
    # 結尾
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>📄 資料來源: {data['sheet_name']}</p>
            <p>⏰ 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function toggleStore(header) {{
            const content = header.nextElementSibling;
            content.classList.toggle('active');
        }}
        
        let allExpanded = false;
        function toggleAll() {{
            const contents = document.querySelectorAll('.store-content');
            allExpanded = !allExpanded;
            contents.forEach(content => {{
                if (allExpanded) {{
                    content.classList.add('active');
                }} else {{
                    content.classList.remove('active');
                }}
            }});
        }}
        
        // 搜尋功能
        document.getElementById('searchBox').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            const sections = document.querySelectorAll('.store-section');
            
            sections.forEach(section => {{
                const storeCode = section.dataset.storeCode.toLowerCase();
                const storeName = section.dataset.storeName.toLowerCase();
                
                if (storeCode.includes(searchTerm) || storeName.includes(searchTerm)) {{
                    section.style.display = 'block';
                }} else {{
                    section.style.display = 'none';
                }}
            }});
        }});
        
        // 預設展開前3個門市
        const firstSections = document.querySelectorAll('.store-content');
        for (let i = 0; i < Math.min(3, firstSections.length); i++) {{
            firstSections[i].classList.add('active');
        }}
    </script>
</body>
</html>
"""
    
    # 寫入檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 報表已生成: {output_file}")
    print(f"   檔案大小: {os.path.getsize(output_file):,} bytes")


def main():
    json_file = "result/store_invoice_detail.json"
    output_file = "result/store_invoice_detail.html"
    
    if not os.path.exists(json_file):
        print(f"❌ 找不到 JSON 檔案: {json_file}")
        print("請先執行 parse_store_invoice.py")
        return
    
    print("📝 正在生成 HTML 報表...")
    generate_html(json_file, output_file)
    print(f"\n🌐 請用瀏覽器開啟: {output_file}")


if __name__ == "__main__":
    main()
