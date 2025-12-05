#!/usr/bin/env python3
"""
离线 OCR 命令行工具
使用 PaddleOCR 进行完全离线的表单识别
"""

import argparse
import json
import sys
from pathlib import Path
from form_parser import FormParser


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="离线 OCR 表单解析工具（基于 PaddleOCR）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础用法
  python3 ocr_parser.py --image form.jpg
  
  # 保存结果
  python3 ocr_parser.py --image form.jpg --output result.json
  
  # 批量处理
  python3 ocr_parser.py --image form1.jpg form2.jpg --output-dir results/
  
  # 使用 GPU 加速
  python3 ocr_parser.py --image form.jpg --use-gpu
  
  # 可视化结果
  python3 ocr_parser.py --image form.jpg --visualize output.jpg
        """
    )
    
    parser.add_argument(
        "--image", "-i",
        nargs="+",
        required=True,
        help="要解析的表单图像路径（可以指定多个）"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径（单个图像时使用）"
    )
    
    parser.add_argument(
        "--output-dir", "-d",
        help="输出目录（批量处理时使用）"
    )
    
    parser.add_argument(
        "--lang", "-l",
        default="ch",
        choices=["ch", "en", "ch_en"],
        help="识别语言（ch=中文, en=英文, ch_en=中英混合）"
    )
    
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="使用 GPU 加速（需要 CUDA 支持）"
    )
    
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="启用图像预处理（提高识别率，适用于低质量图像）"
    )
    
    parser.add_argument(
        "--high-sensitivity",
        action="store_true",
        help="启用高敏感度模式（识别更多文字，可能增加误识别）"
    )
    
    parser.add_argument(
        "--save-preprocessed",
        action="store_true",
        help="保存预处理后的图像"
    )
    
    parser.add_argument(
        "--visualize", "-v",
        help="保存可视化结果图像的路径"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    
    parser.add_argument(
        "--pretty-print",
        action="store_true",
        help="美化打印 JSON 结果"
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化解析器
        if args.verbose:
            print("正在初始化离线 OCR 解析器...")
        
        ocr_parser = FormParser(
            lang=args.lang,
            use_gpu=args.use_gpu,
            enable_preprocessing=args.preprocess,
            high_sensitivity=args.high_sensitivity
        )
        
        # 处理图像
        if len(args.image) == 1:
            # 单个图像
            image_path = args.image[0]
            
            if args.verbose:
                print(f"\n正在解析图像: {image_path}")
            
            result = ocr_parser.parse_form(image_path, save_preprocessed=args.save_preprocessed)
            
            # 可视化
            if args.visualize and result.get("success"):
                ocr_parser.visualize_result(image_path, result, args.visualize)
            
            # 输出结果
            if args.output:
                ocr_parser.save_result(result, args.output)
            else:
                if args.pretty_print:
                    print("\n=== 解析结果 ===")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(result, ensure_ascii=False))
            
            # 显示摘要
            if args.verbose and result.get("success"):
                print("\n✓ 解析成功")
                print(f"  检测文字块: {result.get('total_blocks', 0)}")
                if result.get("fields"):
                    print(f"  提取字段数: {len(result['fields'])}")
        
        else:
            # 多个图像
            output_dir = args.output_dir or "results"
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            if args.verbose:
                print(f"\n批量处理 {len(args.image)} 个图像...")
                print(f"输出目录: {output_dir}\n")
            
            results = ocr_parser.parse_multiple_forms(args.image)
            
            # 保存每个结果
            for i, (image_path, result) in enumerate(zip(args.image, results), 1):
                image_name = Path(image_path).stem
                output_path = f"{output_dir}/{image_name}_result.json"
                ocr_parser.save_result(result, output_path)
                
                # 可视化
                if args.visualize:
                    vis_path = f"{output_dir}/{image_name}_visual.jpg"
                    ocr_parser.visualize_result(image_path, result, vis_path)
            
            print(f"\n✓ 所有结果已保存到: {output_dir}/")
            
            # 统计
            success_count = sum(1 for r in results if r.get("success"))
            print(f"成功: {success_count}/{len(results)}")
    
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
