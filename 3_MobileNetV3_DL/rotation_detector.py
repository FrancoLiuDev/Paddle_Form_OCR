#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MobileNetV3 旋轉角度檢測模型
"""

try:
    import torch
    import torch.nn as nn
    import torchvision.models as models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    models = None

from typing import Tuple
import numpy as np


if TORCH_AVAILABLE:
    class RotationDetector(nn.Module):
        """
        基於 MobileNetV3 的旋轉角度檢測器
        """
        
        def __init__(self, pretrained: bool = True):
            super(RotationDetector, self).__init__()
            
            # 使用 MobileNetV3-Small 作為骨幹網路
            self.backbone = models.mobilenet_v3_small(pretrained=pretrained)
            
            # 替換最後的分類層為回歸層
            # MobileNetV3-Small 的最後一層輸出是 1024
            in_features = self.backbone.classifier[0].in_features
            
            self.backbone.classifier = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.Hardswish(),
                nn.Dropout(0.2),
                nn.Linear(256, 64),
                nn.Hardswish(),
                nn.Dropout(0.2),
                # 輸出 2 個值：sin(angle) 和 cos(angle)
                # 這樣可以更好地處理角度的週期性
                nn.Linear(64, 2),
                nn.Tanh()  # 限制輸出在 [-1, 1]
            )
        
        def forward(self, x):
            """
            前向傳播
            
            Args:
                x: 輸入圖像張量 [batch_size, 3, H, W]
            
            Returns:
                [sin(angle), cos(angle)] 張量 [batch_size, 2]
            """
            return self.backbone(x)
        
        def predict_angle(self, x):
            """
            預測旋轉角度
            
            Args:
                x: 輸入圖像張量 [batch_size, 3, H, W]
            
            Returns:
                角度張量（度） [batch_size]
            """
            with torch.no_grad():
                sin_cos = self.forward(x)
                sin_val = sin_cos[:, 0]
                cos_val = sin_cos[:, 1]
                
                # 從 sin 和 cos 計算角度
                angle_rad = torch.atan2(sin_val, cos_val)
                angle_deg = torch.rad2deg(angle_rad)
                
                return angle_deg
else:
    # PyTorch 不可用時的佔位類
    RotationDetector = None


class SimpleRotationDetector:
    """
    簡單的旋轉檢測器（PCA 方法作為後備）
    當沒有訓練好的模型時使用
    """
    
    def __init__(self):
        try:
            from sklearn.decomposition import PCA
            self.pca = PCA(n_components=2)
            self.available = True
        except ImportError:
            print("警告: scikit-learn 未安裝，無法使用 PCA 方法")
            self.available = False
    
    def predict(self, image: np.ndarray) -> Tuple[float, float]:
        """
        預測旋轉角度
        
        Args:
            image: BGR 格式的圖像
        
        Returns:
            (angle, confidence): 角度和置信度
        """
        if not self.available:
            return 0.0, 0.0
        
        import cv2
        from sklearn.decomposition import PCA
        
        # 轉換為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 邊緣檢測
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 獲取邊緣點
        points = np.column_stack(np.where(edges > 0))
        
        if len(points) < 10:
            return 0.0, 0.0
        
        # PCA 分析
        pca = PCA(n_components=2)
        pca.fit(points)
        
        # 計算角度
        components = pca.components_
        angle_rad = np.arctan2(components[0][0], components[0][1])
        angle_deg = np.degrees(angle_rad)
        
        # 標準化角度
        if angle_deg > 45:
            angle_deg -= 90
        elif angle_deg < -45:
            angle_deg += 90
        
        # 置信度
        explained_variance = pca.explained_variance_ratio_
        confidence = explained_variance[0] / (explained_variance[0] + explained_variance[1])
        
        return angle_deg, confidence


if TORCH_AVAILABLE:
    def load_model(model_path: str, device: str = 'cpu'):
        """
        載入訓練好的模型
        
        Args:
            model_path: 模型檔案路徑
            device: 運算裝置 ('cpu' 或 'cuda')
        
        Returns:
            載入的模型
        """
        model = RotationDetector(pretrained=False)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        return model


    def save_model(model, model_path: str):
        """
        儲存模型
        
        Args:
            model: 要儲存的模型
            model_path: 儲存路徑
        """
        torch.save(model.state_dict(), model_path)
        print(f"模型已儲存至: {model_path}")
else:
    def load_model(model_path: str, device: str = 'cpu'):
        """載入模型（PyTorch 不可用時的佔位函數）"""
        return None
    
    def save_model(model, model_path: str):
        """儲存模型（PyTorch 不可用時的佔位函數）"""
        print("錯誤: PyTorch 未安裝，無法儲存模型")
