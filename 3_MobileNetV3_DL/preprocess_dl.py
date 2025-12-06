#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度學習預處理工具
使用 MobileNetV3 或 PCA 進行旋轉檢測
"""

import cv2
import numpy as np
import argparse
import os
from typing import Tuple

try:
    import torch
    import torchvision.transforms as transforms
    from rotation_detector import RotationDetector, load_model, SimpleRotationDetector
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    transforms = None
    RotationDetector = None
    load_model = None
    from rotation_detector import SimpleRotationDetector
    print("警告: PyTorch 未安裝，將使用 PCA 後備方法")


def preprocess_for_model(image: np.ndarray):
    """
    預處理圖像以供模型使用
    
    Args:
        image: BGR 格式的圖像
    
    Returns:
        處理後的張量 [1, 3, 224, 224]
    """
    if not TORCH_AVAILABLE:
        return None
        
    # 轉換為 RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 定義轉換
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 應用轉換並增加批次維度
    tensor = transform(image_rgb).unsqueeze(0)
    
    return tensor


def detect_angle_deep_learning(image: np.ndarray, model_path: str = None, 
                               verbose: bool = False) -> Tuple[float, float]:
    """
    使用深度學習模型檢測旋轉角度
    
    Returns:
        (angle, confidence): 角度和置信度
    """
    if not TORCH_AVAILABLE:
        if verbose:
            print("  PyTorch 不可用，使用 PCA 方法")
        detector = SimpleRotationDetector()
        return detector.predict(image)
    
    # 檢查是否有模型
    if model_path is None or not os.path.exists(model_path):
        if verbose:
            print("  未找到訓練模型，使用 PCA 方法")
        detector = SimpleRotationDetector()
        return detector.predict(image)
    
    # 載入模型
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if verbose:
        print(f"  使用裝置: {device}")
    
    model = load_model(model_path, device)
    
    # 預處理圖像
    tensor = preprocess_for_model(image).to(device)
    
    # 預測角度
    with torch.no_grad():
        angle = model.predict_angle(tensor).item()
    
    # 模型輸出的置信度（可以通過模型輸出的 sin/cos 值計算）
    confidence = 0.9  # 簡化版本，實際應該從模型輸出計算
    
    return angle, confidence


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """旋轉圖像"""
    if abs(angle) < 0.1:
        return image
    
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h), 
                            flags=cv2.INTER_CUBIC, 
                            borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def preprocess_image(image: np.ndarray, model_path: str = None,
                    enable_rotation: bool = True, 
                    verbose: bool = False) -> Tuple[np.ndarray, float]:
    """
    完整的圖像預處理流程
    
    Returns:
        processed_image: 處理後的圖像
        rotation_angle: 旋轉的角度
    """
    rotation_angle = 0.0
    
    # 1. 自動旋轉
    if enable_rotation:
        if verbose:
            print("\n=== 深度學習旋轉檢測 ===")
        
        angle, confidence = detect_angle_deep_learning(image, model_path, verbose)
        
        if verbose:
            print(f"  檢測角度: {angle:.2f}°")
            print(f"  置信度: {confidence:.2%}")
        
        if abs(angle) > 0.5:
            if verbose:
                print(f"  應用旋轉: {angle:.2f}°")
            image = rotate_image(image, angle)
            rotation_angle = angle
        else:
            if verbose:
                print("  角度過小，無需旋轉")
    
    # 2. 降噪
    if verbose:
        print("\n=== 圖像增強 ===")
        print("  應用降噪...")
    image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    # 3. 灰階轉換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 4. 對比度增強
    if verbose:
        print("  增強對比度...")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 5. 銳化
    if verbose:
        print("  應用銳化...")
    kernel = np.array([[-1, -1, -1],
                      [-1,  9, -1],
                      [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # 轉回彩色
    result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    
    if verbose:
        print("\n預處理完成！")
    
    return result, rotation_angle


def main():
    parser = argparse.ArgumentParser(description='深度學習預處理工具')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像路徑')
    parser.add_argument('--output', '-o', required=True, help='輸出圖像路徑')
    parser.add_argument('--model', '-m', help='模型檔案路徑（.pth）')
    parser.add_argument('--no-rotation', action='store_true', help='停用自動旋轉')
    parser.add_argument('--verbose', '-v', action='store_true', help='顯示詳細輸出')
    
    args = parser.parse_args()
    
    # 讀取圖像
    if not os.path.exists(args.input):
        print(f"錯誤: 找不到輸入檔案 {args.input}")
        return
    
    image = cv2.imread(args.input)
    if image is None:
        print(f"錯誤: 無法讀取圖像 {args.input}")
        return
    
    if args.verbose:
        print(f"讀取圖像: {args.input}")
        print(f"圖像尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 預處理
    processed, rotation_angle = preprocess_image(
        image, 
        model_path=args.model,
        enable_rotation=not args.no_rotation,
        verbose=args.verbose
    )
    
    # 儲存結果
    cv2.imwrite(args.output, processed)
    
    if args.verbose:
        print(f"\n處理完成！")
        print(f"旋轉角度: {rotation_angle:.2f}°")
        print(f"輸出檔案: {args.output}")
    else:
        print(f"已儲存至: {args.output} (旋轉 {rotation_angle:.2f}°)")


if __name__ == '__main__':
    main()
