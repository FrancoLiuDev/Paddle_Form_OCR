#!/usr/bin/env python3
"""
OCR 效果测试脚本
对比预处理前后的识别效果
"""

import sys
from pathlib import Path
from form_parser import FormParser
import json


def test_ocr_with_preprocessing(image_path: str):
    """
    测试预处理对 OCR 识别效果的影响
    
    Args:
        image_path: 图像路径
    """
    print("=" * 80)
    print("OCR 识别效果对比测试")
    print("=" * 80)
    print(f"测试图像: {image_path}\n")
    
    # 测试 1: 标准模式
    print("📋 测试 1: 标准识别（不使用预处理和高敏感度）")
    print("-" * 80)
    parser1 = FormParser(enable_preprocessing=False, high_sensitivity=False)
    result1 = parser1.parse_form(image_path)
    
    if result1['success']:
        print(f"✓ 识别文字块: {result1['total_blocks']}")
        print(f"✓ 平均置信度: {result1['average_confidence']:.2%}")
        print(f"\n识别文字内容:")
        print("-" * 40)
        print(result1['full_text'])
        print("-" * 40)
    else:
        print(f"✗ 识别失败: {result1['error']}")
    
    # 测试 2: 使用预处理
    print("\n📋 测试 2: 启用图像预处理")
    print("-" * 80)
    parser2 = FormParser(enable_preprocessing=True, high_sensitivity=False)
    result2 = parser2.parse_form(image_path, save_preprocessed=True)
    
    if result2['success']:
        print(f"✓ 识别文字块: {result2['total_blocks']}")
        print(f"✓ 平均置信度: {result2['average_confidence']:.2%}")
        print(f"\n识别文字内容:")
        print("-" * 40)
        print(result2['full_text'])
        print("-" * 40)
    else:
        print(f"✗ 识别失败: {result2['error']}")
    
    # 测试 3: 使用高敏感度
    print("\n📋 测试 3: 启用高敏感度模式")
    print("-" * 80)
    parser3 = FormParser(enable_preprocessing=False, high_sensitivity=True)
    result3 = parser3.parse_form(image_path)
    
    if result3['success']:
        print(f"✓ 识别文字块: {result3['total_blocks']}")
        print(f"✓ 平均置信度: {result3['average_confidence']:.2%}")
        print(f"\n识别文字内容:")
        print("-" * 40)
        print(result3['full_text'])
        print("-" * 40)
    else:
        print(f"✗ 识别失败: {result3['error']}")
    
    # 测试 4: 预处理 + 高敏感度（终极模式）
    print("\n📋 测试 4: 预处理 + 高敏感度（终极模式）")
    print("-" * 80)
    parser4 = FormParser(enable_preprocessing=True, high_sensitivity=True)
    result4 = parser4.parse_form(image_path)
    
    if result4['success']:
        print(f"✓ 识别文字块: {result4['total_blocks']}")
        print(f"✓ 平均置信度: {result4['average_confidence']:.2%}")
        print(f"\n识别文字内容:")
        print("-" * 40)
        print(result4['full_text'])
        print("-" * 40)
    else:
        print(f"✗ 识别失败: {result4['error']}")
    
    # 对比分析
    print("\n" + "=" * 80)
    print("📊 对比分析")
    print("=" * 80)
    
    results = [
        ("标准模式", result1),
        ("预处理模式", result2),
        ("高敏感度模式", result3),
        ("终极模式（预处理+高敏感度）", result4)
    ]
    
    success_results = [(name, r) for name, r in results if r['success']]
    
    if success_results:
        # 显示识别文字块数量对比
        print("\n识别文字块数量对比:")
        max_blocks = max(r['total_blocks'] for _, r in success_results)
        for name, r in success_results:
            blocks = r['total_blocks']
            bar = "█" * int(blocks / max_blocks * 40)
            print(f"  {name:25s} {blocks:3d} {bar}")
        
        # 显示平均置信度对比
        print("\n平均置信度对比:")
        for name, r in success_results:
            conf = r['average_confidence']
            bar = "█" * int(conf * 40)
            print(f"  {name:25s} {conf:.2%} {bar}")
        
        # 找出最佳模式
        best_mode = max(success_results, key=lambda x: x[1]['total_blocks'])
        print(f"\n🏆 最佳模式: {best_mode[0]}")
        print(f"   识别文字块: {best_mode[1]['total_blocks']}")
        print(f"   平均置信度: {best_mode[1]['average_confidence']:.2%}")
        
        # 找出新识别出来的文字
        text1_set = set(b['text'] for b in result1['text_blocks'])
        text2_set = set(b['text'] for b in result2['text_blocks'])
        new_texts = text2_set - text1_set
        
        if new_texts:
            print(f"\n✨ 预处理后新识别出的文字 ({len(new_texts)} 个):")
            for text in sorted(new_texts):
                print(f"   • {text}")
        
        # 找出置信度提升的文字
        print(f"\n📈 置信度提升的文字:")
        text_conf_map1 = {b['text']: b['confidence'] for b in result1['text_blocks']}
        text_conf_map2 = {b['text']: b['confidence'] for b in result2['text_blocks']}
        
        improved = []
        for text in text_conf_map1:
            if text in text_conf_map2:
                diff = text_conf_map2[text] - text_conf_map1[text]
                if diff > 0.05:  # 提升超过 5%
                    improved.append((text, text_conf_map1[text], text_conf_map2[text], diff))
        
        if improved:
            improved.sort(key=lambda x: x[3], reverse=True)
            for text, conf1, conf2, diff in improved[:5]:  # 显示前 5 个
                print(f"   • {text}: {conf1:.2%} → {conf2:.2%} (+{diff:.2%})")
    
    # 建议
    print("\n" + "=" * 80)
    print("💡 建议")
    print("=" * 80)
    
    if len(success_results) == 4:
        best_blocks = best_mode[1]['total_blocks']
        standard_blocks = result1['total_blocks']
        improvement = ((best_blocks - standard_blocks) / standard_blocks * 100) if standard_blocks > 0 else 0
        
        if improvement > 20:
            print(f"✅ {best_mode[0]} 效果显著，识别率提升 {improvement:.1f}%")
            print("\n推荐使用方法:")
            if "终极" in best_mode[0]:
                print("  python3 ocr_parser.py --image your_form.jpg --preprocess --high-sensitivity")
                print("\n或在代码中:")
                print("  parser = FormParser(enable_preprocessing=True, high_sensitivity=True)")
            elif "高敏感度" in best_mode[0]:
                print("  python3 ocr_parser.py --image your_form.jpg --high-sensitivity")
                print("\n或在代码中:")
                print("  parser = FormParser(high_sensitivity=True)")
            elif "预处理" in best_mode[0]:
                print("  python3 ocr_parser.py --image your_form.jpg --preprocess")
                print("\n或在代码中:")
                print("  parser = FormParser(enable_preprocessing=True)")
        elif improvement > 5:
            print(f"✅ {best_mode[0]} 有一定改善，识别率提升 {improvement:.1f}%")
            print("   可以根据需要选择使用")
        else:
            print("ℹ️  各种模式效果相近，当前图像质量已经较好")
            print("   可直接使用标准模式识别")
    else:
        # 有失败的情况
        print("⚠️  部分模式识别失败")
        if len(success_results) > 0:
            print(f"✅ {best_mode[0]} 效果最好")
            print("   建议使用该模式")
        else:
            print("❌ 所有模式都无法识别，建议:")
            print("   1. 检查图像质量")
            print("   2. 提高图像分辨率")
            print("   3. 改善拍摄/扫描条件")
            print("   4. 参考 OCR_IMPROVEMENT_GUIDE.md 进行手动调整")
    
    # 保存对比结果
    comparison_file = f"{Path(image_path).stem}_comparison.json"
    comparison_data = {
        "image_path": image_path,
        "standard_mode": {
            "success": result1['success'],
            "total_blocks": result1.get('total_blocks', 0),
            "average_confidence": result1.get('average_confidence', 0)
        },
        "preprocessing_mode": {
            "success": result2['success'],
            "total_blocks": result2.get('total_blocks', 0),
            "average_confidence": result2.get('average_confidence', 0)
        },
        "high_sensitivity_mode": {
            "success": result3['success'],
            "total_blocks": result3.get('total_blocks', 0),
            "average_confidence": result3.get('average_confidence', 0)
        },
        "ultimate_mode": {
            "success": result4['success'],
            "total_blocks": result4.get('total_blocks', 0),
            "average_confidence": result4.get('average_confidence', 0)
        }
    }
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 对比数据已保存到: {comparison_file}")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 test_ocr.py <image_path>")
        print("\n示例:")
        print("  python3 test_ocr.py examples/form.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"错误: 图像文件不存在: {image_path}")
        sys.exit(1)
    
    try:
        test_ocr_with_preprocessing(image_path)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
