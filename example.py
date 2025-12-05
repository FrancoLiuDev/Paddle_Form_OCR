#!/usr/bin/env python3
"""
使用示例
"""

from form_parser import FormParser

print("=" * 60)
print("离线 OCR 表单解析器 - 使用示例")
print("=" * 60)

# 示例 1: 基础用法
print("\n示例 1: 基础用法")
print("-" * 60)
print("""
from form_parser import FormParser

# 初始化解析器
parser = FormParser()

# 解析表单
result = parser.parse_form("form.jpg")

# 查看结果
print(result)
""")

# 示例 2: 保存结果
print("\n示例 2: 保存结果")
print("-" * 60)
print("""
# 解析并保存
result = parser.parse_form("form.jpg")
parser.save_result(result, "output.json")
""")

# 示例 3: 批量处理
print("\n示例 3: 批量处理")
print("-" * 60)
print("""
# 批量处理多个表单
image_list = ["form1.jpg", "form2.jpg", "form3.jpg"]
results = parser.parse_multiple_forms(image_list)

# 保存所有结果
for i, result in enumerate(results, 1):
    parser.save_result(result, f"result_{i}.json")
""")

# 示例 4: 可视化
print("\n示例 4: 可视化结果")
print("-" * 60)
print("""
# 解析并生成可视化图像
result = parser.parse_form("form.jpg")
parser.visualize_result("form.jpg", result, "visual.jpg")
""")

# 示例 5: 使用 GPU
print("\n示例 5: 使用 GPU 加速")
print("-" * 60)
print("""
# 启用 GPU（需要 NVIDIA GPU + CUDA）
parser = FormParser(use_gpu=True)
result = parser.parse_form("form.jpg")
""")

# 示例 6: 中英文混合
print("\n示例 6: 中英文混合识别")
print("-" * 60)
print("""
# 中英文混合模式
parser = FormParser(lang='ch_en')
result = parser.parse_form("form.jpg")
""")

print("\n" + "=" * 60)
print("将图像放到 examples/ 目录，然后运行：")
print("  python3 ocr_parser.py --image examples/your_form.jpg")
print("=" * 60)
