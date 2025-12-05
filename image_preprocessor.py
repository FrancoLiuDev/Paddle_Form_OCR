"""
图像预处理模块
用于提高 OCR 识别率
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class ImagePreprocessor:
    """图像预处理器，提升 OCR 识别质量"""
    
    @staticmethod
    def enhance_image(image_path: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        综合图像增强处理
        
        Args:
            image_path: 输入图像路径
            output_path: 可选的输出路径，如果提供则保存处理后的图像
            
        Returns:
            处理后的图像数组
        """
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 应用增强流程
        enhanced = ImagePreprocessor._apply_enhancement_pipeline(img)
        
        # 保存处理后的图像（如果指定了输出路径）
        if output_path:
            cv2.imwrite(output_path, enhanced)
            print(f"预处理后的图像已保存到: {output_path}")
        
        return enhanced
    
    @staticmethod
    def _apply_enhancement_pipeline(img: np.ndarray) -> np.ndarray:
        """
        应用完整的增强流程
        
        Args:
            img: 输入图像
            
        Returns:
            增强后的图像
        """
        # 1. 去噪
        img = ImagePreprocessor.denoise(img)
        
        # 2. 灰度转换
        gray = ImagePreprocessor.to_grayscale(img)
        
        # 3. 对比度增强
        enhanced = ImagePreprocessor.enhance_contrast(gray)
        
        # 4. 自适应二值化（可选，对低质量图像有帮助）
        # enhanced = ImagePreprocessor.adaptive_threshold(enhanced)
        
        # 5. 锐化
        sharpened = ImagePreprocessor.sharpen(enhanced)
        
        return sharpened
    
    @staticmethod
    def denoise(img: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        去除图像噪点
        
        Args:
            img: 输入图像
            strength: 去噪强度 (1-20)
            
        Returns:
            去噪后的图像
        """
        return cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)
    
    @staticmethod
    def to_grayscale(img: np.ndarray) -> np.ndarray:
        """
        转换为灰度图
        
        Args:
            img: 输入图像
            
        Returns:
            灰度图像
        """
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    @staticmethod
    def enhance_contrast(img: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
        """
        使用 CLAHE 增强对比度
        
        Args:
            img: 输入图像（灰度图）
            clip_limit: 对比度限制
            tile_size: 网格大小
            
        Returns:
            增强后的图像
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        return clahe.apply(img)
    
    @staticmethod
    def adaptive_threshold(img: np.ndarray, block_size: int = 11, c: int = 2) -> np.ndarray:
        """
        自适应二值化（对光照不均匀的图像有效）
        
        Args:
            img: 输入图像（灰度图）
            block_size: 块大小（必须是奇数）
            c: 常数偏移
            
        Returns:
            二值化后的图像
        """
        return cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, block_size, c
        )
    
    @staticmethod
    def sharpen(img: np.ndarray, kernel_size: Tuple[int, int] = (5, 5)) -> np.ndarray:
        """
        锐化图像
        
        Args:
            img: 输入图像
            kernel_size: 卷积核大小
            
        Returns:
            锐化后的图像
        """
        # 高斯模糊
        blurred = cv2.GaussianBlur(img, kernel_size, 0)
        # 锐化（原图 - 模糊图）
        sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
        return sharpened
    
    @staticmethod
    def resize_for_ocr(img: np.ndarray, target_height: int = 1000) -> np.ndarray:
        """
        调整图像大小以优化 OCR 识别
        （太小识别不清，太大处理慢）
        
        Args:
            img: 输入图像
            target_height: 目标高度（像素）
            
        Returns:
            调整大小后的图像
        """
        height, width = img.shape[:2]
        
        # 如果图像太小，放大
        if height < target_height:
            scale = target_height / height
            new_width = int(width * scale)
            return cv2.resize(img, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
        
        # 如果图像太大，缩小
        elif height > target_height * 2:
            scale = target_height / height
            new_width = int(width * scale)
            return cv2.resize(img, (new_width, target_height), interpolation=cv2.INTER_AREA)
        
        return img
    
    @staticmethod
    def deskew(img: np.ndarray) -> np.ndarray:
        """
        纠正图像倾斜
        
        Args:
            img: 输入图像
            
        Returns:
            纠正后的图像
        """
        # 转换为灰度图
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 霍夫变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return img
        
        # 计算平均角度
        angles = []
        for rho, theta in lines[:, 0]:
            angle = (theta * 180 / np.pi) - 90
            angles.append(angle)
        
        median_angle = np.median(angles)
        
        # 如果倾斜角度太小，不处理
        if abs(median_angle) < 0.5:
            return img
        
        # 旋转图像
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_REPLICATE)
        
        print(f"图像倾斜已纠正，角度: {median_angle:.2f}°")
        return rotated
    
    @staticmethod
    def remove_background(img: np.ndarray) -> np.ndarray:
        """
        去除背景噪声（适用于有复杂背景的表单）
        
        Args:
            img: 输入图像
            
        Returns:
            去除背景后的图像
        """
        # 转换为灰度图
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Otsu 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary


# 使用示例
if __name__ == "__main__":
    print("图像预处理模块")
    print("=" * 60)
    print("\n使用示例:")
    print("""
from image_preprocessor import ImagePreprocessor

# 增强图像
preprocessor = ImagePreprocessor()
enhanced_img = preprocessor.enhance_image("input.jpg", "enhanced.jpg")

# 或者在 FormParser 中使用预处理
from form_parser import FormParser
parser = FormParser(enable_preprocessing=True)
result = parser.parse_form("form.jpg")
""")
