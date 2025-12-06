#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訓練旋轉角度檢測模型
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from rotation_detector import RotationDetector, save_model
import cv2
import numpy as np
import json
import os
from typing import Tuple, List
import argparse
from tqdm import tqdm


class RotationDataset(Dataset):
    """
    旋轉角度檢測數據集
    """
    
    def __init__(self, data_dir: str, annotations_file: str, transform=None, augment: bool = True):
        """
        Args:
            data_dir: 圖像目錄
            annotations_file: 標註檔案（JSON 格式）
            transform: 圖像轉換
            augment: 是否進行數據增強
        """
        self.data_dir = data_dir
        self.augment = augment
        self.transform = transform if transform else self.get_default_transform()
        
        # 載入標註
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
        
        self.image_files = list(self.annotations.keys())
    
    def get_default_transform(self):
        """預設圖像轉換"""
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor]:
        # 讀取圖像
        img_name = self.image_files[idx]
        img_path = os.path.join(self.data_dir, img_name)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 獲取角度標註
        angle = self.annotations[img_name]
        
        # 數據增強：隨機旋轉
        if self.augment:
            random_angle = np.random.uniform(-10, 10)
            angle += random_angle
            
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, -random_angle, 1.0)
            image = cv2.warpAffine(image, matrix, (w, h))
        
        # 轉換圖像
        image_tensor = self.transform(image)
        
        # 將角度轉換為 sin 和 cos
        angle_rad = np.radians(angle)
        sin_val = np.sin(angle_rad)
        cos_val = np.cos(angle_rad)
        
        target = torch.tensor([sin_val, cos_val], dtype=torch.float32)
        
        return image_tensor, target


def train_epoch(model: nn.Module, dataloader: DataLoader, 
               criterion: nn.Module, optimizer: optim.Optimizer, 
               device: str) -> float:
    """
    訓練一個 epoch
    """
    model.train()
    total_loss = 0.0
    
    for images, targets in tqdm(dataloader, desc='Training'):
        images = images.to(device)
        targets = targets.to(device)
        
        # 前向傳播
        outputs = model(images)
        loss = criterion(outputs, targets)
        
        # 反向傳播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def validate(model: nn.Module, dataloader: DataLoader, 
            criterion: nn.Module, device: str) -> Tuple[float, float]:
    """
    驗證模型
    
    Returns:
        (loss, mae): 損失和平均絕對誤差（度）
    """
    model.eval()
    total_loss = 0.0
    total_mae = 0.0
    
    with torch.no_grad():
        for images, targets in tqdm(dataloader, desc='Validation'):
            images = images.to(device)
            targets = targets.to(device)
            
            # 前向傳播
            outputs = model(images)
            loss = criterion(outputs, targets)
            
            # 計算角度誤差
            pred_sin = outputs[:, 0]
            pred_cos = outputs[:, 1]
            pred_angle = torch.rad2deg(torch.atan2(pred_sin, pred_cos))
            
            target_sin = targets[:, 0]
            target_cos = targets[:, 1]
            target_angle = torch.rad2deg(torch.atan2(target_sin, target_cos))
            
            mae = torch.abs(pred_angle - target_angle).mean()
            
            total_loss += loss.item()
            total_mae += mae.item()
    
    return total_loss / len(dataloader), total_mae / len(dataloader)


def main():
    parser = argparse.ArgumentParser(description='訓練旋轉角度檢測模型')
    parser.add_argument('--data-dir', required=True, help='訓練數據目錄')
    parser.add_argument('--annotations', default='annotations.json', help='標註檔案')
    parser.add_argument('--val-split', type=float, default=0.2, help='驗證集比例')
    parser.add_argument('--epochs', type=int, default=50, help='訓練輪數')
    parser.add_argument('--batch-size', type=int, default=32, help='批次大小')
    parser.add_argument('--lr', type=float, default=0.001, help='學習率')
    parser.add_argument('--output', default='rotation_model.pth', help='輸出模型路徑')
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu', 
                       help='訓練裝置')
    
    args = parser.parse_args()
    
    print(f"使用裝置: {args.device}")
    
    # 載入數據集
    annotations_path = os.path.join(args.data_dir, args.annotations)
    full_dataset = RotationDataset(
        data_dir=os.path.join(args.data_dir, 'images'),
        annotations_file=annotations_path,
        augment=True
    )
    
    # 分割訓練集和驗證集
    val_size = int(len(full_dataset) * args.val_split)
    train_size = len(full_dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size]
    )
    
    print(f"訓練集大小: {train_size}")
    print(f"驗證集大小: {val_size}")
    
    # 創建數據加載器
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, 
                            shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, 
                          shuffle=False, num_workers=4)
    
    # 創建模型
    model = RotationDetector(pretrained=True).to(args.device)
    
    # 損失函數和優化器
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', 
                                                     factor=0.5, patience=5)
    
    # 訓練循環
    best_val_mae = float('inf')
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")
        
        # 訓練
        train_loss = train_epoch(model, train_loader, criterion, optimizer, args.device)
        
        # 驗證
        val_loss, val_mae = validate(model, val_loader, criterion, args.device)
        
        # 更新學習率
        scheduler.step(val_loss)
        
        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val MAE: {val_mae:.2f}°")
        
        # 儲存最佳模型
        if val_mae < best_val_mae:
            best_val_mae = val_mae
            save_model(model, args.output)
            print(f"✓ 儲存最佳模型 (MAE: {val_mae:.2f}°)")
    
    print(f"\n訓練完成！最佳驗證 MAE: {best_val_mae:.2f}°")
    print(f"模型已儲存至: {args.output}")


if __name__ == '__main__':
    main()
