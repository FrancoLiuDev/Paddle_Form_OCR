#!/usr/bin/env python3
"""
改善 OCR 识别率的实际使用示例
"""

from form_parser import FormParser
from image_preprocessor import ImagePreprocessor
import cv2

print("=" * 80)
print("OCR 识别率改善示例")
print("=" * 80)

# ============================================================================
# 示例 1: 最简单的方法 - 启用预处理
# ============================================================================
print("\n【示例 1】最简单有效的方法：启用预处理")
print("-" * 80)
print("""
如果有些内文没有辨识出来，最简单的方法是启用预处理：

from form_parser import FormParser

# 启用预处理
parser = FormParser(enable_preprocessing=True)
result = parser.parse_form("form.jpg")

# 查看识别结果
print(f"识别到 {result['total_blocks']} 个文字块")
print(f"平均置信度: {result['average_confidence']:.2%}")
print(result['full_text'])
""")

# ============================================================================
# 示例 2: 对比预处理效果
# ============================================================================
print("\n【示例 2】对比预处理前后的效果")
print("-" * 80)
print("""
from form_parser import FormParser

# 不使用预处理
parser1 = FormParser(enable_preprocessing=False)
result1 = parser1.parse_form("form.jpg")

# 使用预处理
parser2 = FormParser(enable_preprocessing=True)
result2 = parser2.parse_form("form.jpg")

# 对比
print(f"不使用预处理: {result1['total_blocks']} 个文字块")
print(f"使用预处理:   {result2['total_blocks']} 个文字块")

# 或者直接使用测试脚本
# python3 test_ocr.py form.jpg
""")

# ============================================================================
# 示例 3: 手动预处理（高级用法）
# ============================================================================
print("\n【示例 3】手动预处理图像（针对特殊情况）")
print("-" * 80)
print("""
from image_preprocessor import ImagePreprocessor
import cv2

preprocessor = ImagePreprocessor()

# 读取图像
img = cv2.imread("form.jpg")

# 方案 A: 一键增强（推荐）
enhanced = preprocessor.enhance_image("form.jpg", "enhanced.jpg")

# 方案 B: 逐步处理（可自定义参数）
img = preprocessor.denoise(img, strength=15)         # 去噪
gray = preprocessor.to_grayscale(img)                # 灰度化
enhanced = preprocessor.enhance_contrast(gray)       # 增强对比度
sharpened = preprocessor.sharpen(enhanced)           # 锐化

# 保存处理后的图像
cv2.imwrite("processed.jpg", sharpened)

# 使用处理后的图像进行 OCR
from form_parser import FormParser
parser = FormParser()
result = parser.parse_form("processed.jpg")
""")

# ============================================================================
# 示例 4: 针对不同问题的解决方案
# ============================================================================
print("\n【示例 4】针对不同问题的解决方案")
print("-" * 80)
print("""
from image_preprocessor import ImagePreprocessor
import cv2

preprocessor = ImagePreprocessor()
img = cv2.imread("form.jpg")

# 问题 1: 图像模糊 → 去噪 + 锐化
img = preprocessor.denoise(img, strength=20)
img = preprocessor.sharpen(img)

# 问题 2: 光照不均 → 自适应二值化
gray = preprocessor.to_grayscale(img)
binary = preprocessor.adaptive_threshold(gray, block_size=15, c=2)

# 问题 3: 图像倾斜 → 纠正倾斜
deskewed = preprocessor.deskew(img)

# 问题 4: 图像太小 → 放大图像
resized = preprocessor.resize_for_ocr(img, target_height=2000)

# 问题 5: 复杂背景 → 去除背景
no_bg = preprocessor.remove_background(img)

# 保存并识别
cv2.imwrite("fixed.jpg", img)

from form_parser import FormParser
parser = FormParser()
result = parser.parse_form("fixed.jpg")
""")

# ============================================================================
# 示例 5: 命令行使用
# ============================================================================
print("\n【示例 5】命令行使用（最方便）")
print("-" * 80)
print("""
# 基础识别
python3 ocr_parser.py --image form.jpg

# 启用预处理
python3 ocr_parser.py --image form.jpg --preprocess

# 启用预处理 + 保存处理后的图像
python3 ocr_parser.py --image form.jpg --preprocess --save-preprocessed

# 启用预处理 + 可视化结果
python3 ocr_parser.py --image form.jpg --preprocess --visualize result.jpg

# 批量处理
python3 ocr_parser.py --image *.jpg --preprocess --output-dir results/

# 测试对比效果
python3 test_ocr.py form.jpg
""")

# ============================================================================
# 示例 6: 查看置信度
# ============================================================================
print("\n【示例 6】查看识别置信度（找出识别不佳的部分）")
print("-" * 80)
print("""
from form_parser import FormParser

parser = FormParser(enable_preprocessing=True)
result = parser.parse_form("form.jpg")

# 查看所有文字块的置信度
for block in result['text_blocks']:
    conf = block['confidence']
    text = block['text']
    
    # 标记低置信度的文字
    if conf < 0.8:
        print(f"⚠️  低置信度: {text} ({conf:.2%})")
    else:
        print(f"✓  {text} ({conf:.2%})")

# 查看平均置信度
print(f"\\n平均置信度: {result['average_confidence']:.2%}")
""")

# ============================================================================
# 示例 7: 保存结果
# ============================================================================
print("\n【示例 7】保存识别结果")
print("-" * 80)
print("""
from form_parser import FormParser

parser = FormParser(enable_preprocessing=True)
result = parser.parse_form("form.jpg")

# 保存为 JSON
parser.save_result(result, "result.json")

# 生成可视化图像（标注识别框）
parser.visualize_result("form.jpg", result, "visual.jpg", show_text=True)

# 批量处理
images = ["form1.jpg", "form2.jpg", "form3.jpg"]
results = parser.parse_multiple_forms(images)

for i, result in enumerate(results, 1):
    parser.save_result(result, f"result_{i}.json")
""")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 80)
print("💡 总结：改善识别率的推荐流程")
print("=" * 80)
print("""
1. 首先尝试标准识别：
   python3 ocr_parser.py --image form.jpg

2. 如果识别不全，启用预处理：
   python3 ocr_parser.py --image form.jpg --preprocess

3. 对比效果：
   python3 test_ocr.py form.jpg

4. 如果还有问题，查看详细指南：
   cat OCR_IMPROVEMENT_GUIDE.md

5. 针对特殊情况，手动调整预处理参数

大多数情况下，使用 --preprocess 就能解决问题！
""")

print("=" * 80)
print("更多信息请参考:")
print("  • OCR_IMPROVEMENT_GUIDE.md - 完整改善指南")
print("  • python3 ocr_parser.py --help - 命令行帮助")
print("  • python3 test_ocr.py <image> - 效果对比测试")
print("=" * 80)
