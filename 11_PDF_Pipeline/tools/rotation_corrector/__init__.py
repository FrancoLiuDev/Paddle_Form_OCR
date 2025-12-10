"""
旋轉校正工具模組
使用 Hough Line Detection 檢測並校正圖片角度
"""

from pathlib import Path
import sys
import subprocess
import cv2
import numpy as np


class RotationCorrector:
    """圖片旋轉校正器"""
    
    def __init__(self, degree=30, skip_threshold=5.0):
        """初始化校正器
        
        Args:
            degree: 角度過濾範圍，預設 30
            skip_threshold: 跳過旋轉的角度閾值（絕對值），預設 5.0 度
        """
        self.degree = degree
        self.skip_threshold = skip_threshold
        self.script_path = Path(__file__).parent / "preprocess_hough.py"
        
        if not self.script_path.exists():
            raise FileNotFoundError(f"找不到處理腳本: {self.script_path}")
    
    def correct_single(self, image_path, output_path, verbose=False):
        """校正單張圖片
        
        Args:
            image_path: 輸入圖片路徑
            output_path: 輸出圖片路徑
            verbose: 是否顯示詳細資訊
            
        Returns:
            tuple: (success, angle, message, skipped)
        """
        image_path = Path(image_path).absolute()
        output_path = Path(output_path).absolute()
        
        if not image_path.exists():
            return False, None, f"圖片不存在: {image_path}", False
        
        # 確保輸出目錄存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 執行旋轉校正
        cmd = [
            sys.executable,
            str(self.script_path),
            "--input", str(image_path),
            "--output", str(output_path),
            "--degree", str(self.degree),
            "--show-lines"  # 必須啟用以輸出角度資訊
        ]
        
        if verbose:
            cmd.append("--verbose")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return False, None, f"校正失敗: {error_msg}", False
            
            # 從輸出中提取角度資訊
            angle = None
            for line in result.stdout.split('\n'):
                if '最終輸出角度' in line or '最多出現的角度' in line:
                    # 提取角度數值
                    import re
                    match = re.search(r'([-+]?\d+\.?\d*)°', line)
                    if match:
                        angle = float(match.group(1))
                        break
            
            # 如果沒有檢測到角度，視為錯誤
            if angle is None:
                return False, None, "無法檢測到角度資訊", False
            
            # 檢查角度是否在閾值內
            if abs(angle) <= self.skip_threshold:
                # 角度在 ±skip_threshold 內，使用原圖
                if image_path != output_path:
                    import shutil
                    # 如果已經產生了旋轉後的圖片，用原圖替換
                    shutil.copy2(str(image_path), str(output_path))
                
                return True, angle, f"角度 {angle:.2f}° 在 ±{self.skip_threshold}° 內，跳過旋轉", True
            
            # 檢查輸出檔案
            if not output_path.exists():
                return False, angle, "處理完成但未產生輸出檔案", False
            
            return True, angle, f"成功校正 (角度: {angle:.2f}°)", False
            
        except subprocess.TimeoutExpired:
            return False, None, "處理超時（超過 60 秒）", False
        except Exception as e:
            return False, None, f"執行錯誤: {str(e)}", False
    
    def correct_batch(self, input_dir, output_dir=None, inplace=False, verbose=False):
        """批次校正圖片
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄（如果為 None 且 inplace=True，則覆蓋原圖）
            inplace: 是否覆蓋原圖
            verbose: 是否顯示詳細資訊
            
        Returns:
            tuple: (success_count, total_count, results)
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            return 0, 0, []
        
        # 如果覆蓋原圖，輸出目錄就是輸入目錄
        if inplace:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir) if output_dir else input_dir
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集所有圖片
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(input_dir.glob(ext))
        
        image_files = sorted(image_files)
        
        if len(image_files) == 0:
            return 0, 0, []
        
        results = []
        success_count = 0
        skipped_count = 0
        
        for img_file in image_files:
            output_file = output_dir / img_file.name
            
            success, angle, message, skipped = self.correct_single(
                img_file,
                output_file,
                verbose=verbose
            )
            
            if success:
                success_count += 1
            
            if skipped:
                skipped_count += 1
            
            results.append({
                'file': img_file.name,
                'success': success,
                'angle': angle,
                'message': message,
                'skipped': skipped
            })
        
        return success_count, len(image_files), results


__all__ = ['RotationCorrector']
