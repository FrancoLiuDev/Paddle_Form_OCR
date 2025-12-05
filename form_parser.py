"""
离线 OCR 表单解析器
使用 PaddleOCR 进行完全离线的文字识别
无需 API Key，无需网络连接
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from paddleocr import PaddleOCR
import cv2
import numpy as np
from image_preprocessor import ImagePreprocessor


class FormParser:
    """离线表单解析器类（使用 PaddleOCR）"""
    
    def __init__(self, lang: str = 'ch', use_gpu: bool = False, enable_preprocessing: bool = False, 
                 high_sensitivity: bool = False):
        """
        初始化离线表单解析器
        
        Args:
            lang: 语言类型 ('ch'=中文, 'en'=英文, 'ch_en'=中英文混合)
            use_gpu: 是否使用 GPU 加速
            enable_preprocessing: 是否启用图像预处理（提高识别率）
            high_sensitivity: 是否启用高敏感度模式（识别更多文字，但可能增加误识别）
        """
        print(f"正在初始化 PaddleOCR（语言: {lang}, GPU: {use_gpu}）...")
        if high_sensitivity:
            print("✨ 已启用高敏感度模式（可识别更多文字）")
        print("首次运行会自动下载模型文件（约 20-30MB）...")
        
        # 根据敏感度设置参数
        if high_sensitivity:
            # 高敏感度参数（降低阈值，识别更多文字）
            det_db_thresh = 0.2          # 降低检测阈值（默认 0.3）
            det_db_box_thresh = 0.4      # 降低文本框阈值（默认 0.6）
            det_db_unclip_ratio = 2.0    # 增加文本框扩展比例（默认 1.5）
            rec_batch_num = 8            # 增加批次大小
        else:
            # 标准参数（平衡准确率和召回率）
            det_db_thresh = 0.3
            det_db_box_thresh = 0.5
            det_db_unclip_ratio = 1.6
            rec_batch_num = 6
        
        # 初始化 PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=True,              # 使用角度分类器
            lang=lang,                       # 语言
            use_gpu=use_gpu,                 # 是否使用 GPU
            show_log=False,                  # 不显示详细日志
            det_db_thresh=det_db_thresh,     # 检测阈值
            det_db_box_thresh=det_db_box_thresh,  # 文本框阈值
            det_db_unclip_ratio=det_db_unclip_ratio,  # 文本框扩展比例
            rec_batch_num=rec_batch_num,     # 识别批次大小
            max_text_length=512              # 最大文本长度
        )
        
        self.enable_preprocessing = enable_preprocessing
        self.high_sensitivity = high_sensitivity
        self.preprocessor = ImagePreprocessor() if enable_preprocessing else None
        
        print("✓ PaddleOCR 初始化完成")
        if enable_preprocessing:
            print("✓ 图像预处理已启用")
    
    def parse_form(self, image_path: str, save_preprocessed: bool = False) -> Dict[str, Any]:
        """
        解析表单图像（完全离线）
        
        Args:
            image_path: 表单图像路径
            save_preprocessed: 是否保存预处理后的图像
            
        Returns:
            解析结果字典
        """
        # 验证文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        try:
            print(f"正在识别: {image_path}")
            
            # 如果启用预处理，先处理图像
            processed_image_path = image_path
            if self.enable_preprocessing:
                print("  > 正在进行图像预处理...")
                temp_dir = os.path.join(os.path.dirname(image_path), ".preprocessed")
                os.makedirs(temp_dir, exist_ok=True)
                
                processed_image_path = os.path.join(
                    temp_dir, 
                    f"preprocessed_{os.path.basename(image_path)}"
                )
                
                self.preprocessor.enhance_image(image_path, processed_image_path)
                print("  ✓ 图像预处理完成")
                
                if save_preprocessed:
                    final_path = image_path.replace(".", "_preprocessed.")
                    import shutil
                    shutil.copy(processed_image_path, final_path)
                    print(f"  ✓ 预处理图像已保存到: {final_path}")
            
            # 执行 OCR 识别
            result = self.ocr.ocr(processed_image_path, cls=True)
            
            # 解析结果
            if not result or not result[0]:
                return {
                    "success": False,
                    "error": "未检测到文字",
                    "image_path": image_path,
                    "suggestion": "尝试：1) 启用预处理 enable_preprocessing=True  2) 启用高敏感度 high_sensitivity=True"
                }
            
            # 提取文字和位置信息
            text_blocks = []
            full_text = []
            
            for line in result[0]:
                # line[0] 是坐标框, line[1] 是 (文字, 置信度)
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                text_blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "position": box
                })
                
                full_text.append(text)
            
            # 计算平均置信度
            avg_confidence = sum(b["confidence"] for b in text_blocks) / len(text_blocks)
            
            # 尝试提取结构化信息
            fields = self._extract_fields(text_blocks)
            
            return {
                "success": True,
                "image_path": image_path,
                "text_blocks": text_blocks,
                "full_text": "\n".join(full_text),
                "fields": fields,
                "total_blocks": len(text_blocks),
                "average_confidence": round(avg_confidence, 4),
                "preprocessing_enabled": self.enable_preprocessing,
                "high_sensitivity_enabled": self.high_sensitivity,
                "ocr_engine": "PaddleOCR (Offline)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def _extract_fields(self, text_blocks: List[Dict]) -> Dict[str, str]:
        """
        从文字块中提取结构化字段
        
        Args:
            text_blocks: 文字块列表
            
        Returns:
            字段字典
        """
        fields = {}
        
        # 常见的字段标签
        field_keywords = [
            "姓名", "名称", "性别", "年龄", "出生", "日期",
            "身份证", "证件号", "编号", "号码", "电话", "手机",
            "地址", "住址", "单位", "公司", "职业", "职务",
            "金额", "总额", "合计", "税额", "发票号"
        ]
        
        for i, block in enumerate(text_blocks):
            text = block["text"]
            
            # 检查是否包含字段关键词
            for keyword in field_keywords:
                if keyword in text:
                    # 尝试获取后面的值
                    parts = text.split(keyword, 1)
                    if len(parts) > 1 and parts[1].strip():
                        # 值在同一行
                        fields[keyword] = parts[1].strip().rstrip("：:").strip()
                    elif i + 1 < len(text_blocks):
                        # 值可能在下一行
                        next_text = text_blocks[i + 1]["text"]
                        fields[keyword] = next_text.strip()
        
        return fields
    
    def parse_multiple_forms(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量解析多个表单
        
        Args:
            image_paths: 图像路径列表
            
        Returns:
            解析结果列表
        """
        results = []
        total = len(image_paths)
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n[{i}/{total}] 正在处理: {image_path}")
            result = self.parse_form(image_path)
            results.append(result)
            
            if result.get("success"):
                print(f"✓ 识别成功，检测到 {result.get('total_blocks', 0)} 个文字块")
            else:
                print(f"✗ 识别失败: {result.get('error', '未知错误')}")
        
        return results
    
    def save_result(self, result: Dict[str, Any], output_path: str):
        """
        保存解析结果到文件
        
        Args:
            result: 解析结果
            output_path: 输出文件路径
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {output_path}")
    
    def visualize_result(self, image_path: str, result: Dict[str, Any], output_path: str, show_text: bool = False):
        """
        可视化识别结果（在图像上标注文字框）
        
        Args:
            image_path: 原始图像路径
            result: 识别结果
            output_path: 输出图像路径
            show_text: 是否显示文字标注（默认 False，只显示框）
        """
        if not result.get("success") or "text_blocks" not in result:
            print("无法可视化：识别失败或无文字块")
            return
        
        # 读取图像
        image = cv2.imread(image_path)
        
        # 绘制文字框
        for block in result["text_blocks"]:
            box = np.array(block["position"], dtype=np.int32)
            
            # 绘制边框（绿色，2像素宽）
            cv2.polylines(image, [box], True, (0, 255, 0), 2)
            
            # 如果需要显示文字
            if show_text:
                text = block["text"]
                # 在框上方显示文字
                x, y = int(box[0][0]), int(box[0][1]) - 10
                cv2.putText(image, text, (x, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # 保存图像
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        cv2.imwrite(output_path, image)
        print(f"可视化结果已保存到: {output_path}")


if __name__ == "__main__":
    # 测试代码
    parser = FormParser()
    print("\n✅ 离线 OCR 表单解析器已初始化")
    print("\n特点:")
    print("  ✓ 完全离线运行")
    print("  ✓ 无需 API Key")
    print("  ✓ 无需网络连接")
    print("  ✓ 永久免费")
    print("\n使用示例:")
    print('  result = parser.parse_form("examples/form.jpg")')
    print('  parser.save_result(result, "output.json")')
