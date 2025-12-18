"""
基於 deskew 的旋轉校正器
使用 13_Skew_Angle_Detection 模組進行角度檢測
"""

import sys
from pathlib import Path
import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict

# 加入 13_Skew_Angle_Detection 模組路徑
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_SKEW_DETECTOR_DIR = _PROJECT_ROOT / "13_Skew_Angle_Detection"
sys.path.insert(0, str(_SKEW_DETECTOR_DIR))

from skew_detector import SkewDetector


class RotationCorrectorDeskew:
    """
    基於 deskew 的旋轉校正器
    
    使用 13_Skew_Angle_Detection 模組檢測圖片傾斜角度並校正
    """
    
    def __init__(
        self,
        skip_threshold: float = 5.0,
        sigma: float = 3.0,
        num_peaks: int = 20,
        min_angle: float = -45,
        max_angle: float = 45
    ):
        """
        初始化旋轉校正器
        
        Args:
            skip_threshold: 跳過校正的角度閾值（度），小於此值不校正
            sigma: 高斯模糊的 sigma 值
            num_peaks: Hough transform 的峰值數量
            min_angle: 最小檢測角度
            max_angle: 最大檢測角度
        """
        self.skip_threshold = skip_threshold
        
        # 創建 SkewDetector 實例
        self.detector = SkewDetector(
            sigma=sigma,
            num_peaks=num_peaks,
            min_angle=min_angle,
            max_angle=max_angle
        )
        
    def detect_angle(self, image_path: Path) -> Optional[float]:
        """
        檢測圖片的傾斜角度
        
        Args:
            image_path: 圖片檔案路徑
            
        Returns:
            傾斜角度（度），失敗返回 None
        """
        try:
            angle = self.detector.detect_angle_from_file(str(image_path))
            return angle
        except Exception as e:
            print(f"檢測角度失敗 {image_path}: {e}")
            return None
            
    def rotate_image(
        self, 
        image: np.ndarray, 
        angle: float,
        border_value: Tuple[int, int, int] = (255, 255, 255)
    ) -> np.ndarray:
        """
        旋轉圖片
        
        Args:
            image: 輸入圖片
            angle: 旋轉角度（度，deskew 檢測的傾斜角度，直接使用來校正）
            border_value: 邊界填充顏色 (B, G, R)
            
        Returns:
            旋轉後的圖片
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # 計算旋轉矩陣（deskew 返回的角度已經是校正方向，直接使用）
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 應用旋轉
        rotated = cv2.warpAffine(
            image, 
            rotation_matrix, 
            (width, height),
            borderValue=border_value
        )
        
        return rotated
        
    def correct_single(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        inplace: bool = False,
        verbose: bool = False
    ) -> Dict:
        """
        校正單張圖片
        
        Args:
            input_path: 輸入圖片路徑
            output_path: 輸出圖片路徑（如果 inplace=False）
            inplace: 是否覆蓋原圖
            verbose: 是否顯示詳細信息
            
        Returns:
            包含處理結果的字典
        """
        result = {
            'file': input_path.name,
            'success': False,
            'angle': None,
            'skipped': False,
            'message': ''
        }
        
        try:
            # 檢測角度
            angle = self.detect_angle(input_path)
            
            if angle is None:
                result['message'] = '無法檢測角度'
                return result
                
            result['angle'] = angle
            
            # 判斷是否需要校正
            if abs(angle) < self.skip_threshold:
                result['success'] = True
                result['skipped'] = True
                result['message'] = f'角度在閾值內 ({abs(angle):.2f}° < {self.skip_threshold}°)'
                
                if verbose:
                    print(f"⊙ {input_path.name}: 角度 {angle:.2f}° - 跳過校正")
                
                # 如果不是 inplace，仍需複製檔案
                if not inplace and output_path:
                    import shutil
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(input_path, output_path)
                    
                return result
            
            # 讀取圖片
            image = cv2.imread(str(input_path))
            if image is None:
                result['message'] = '無法讀取圖片'
                return result
            
            # 旋轉圖片
            rotated = self.rotate_image(image, angle)
            
            # 儲存結果
            if inplace:
                save_path = input_path
            else:
                if output_path is None:
                    result['message'] = '未指定輸出路徑且非 inplace 模式'
                    return result
                save_path = output_path
                save_path.parent.mkdir(parents=True, exist_ok=True)
            
            cv2.imwrite(str(save_path), rotated)
            
            result['success'] = True
            result['message'] = f'已校正 {angle:.2f}°'
            
            if verbose:
                print(f"✓ {input_path.name}: 角度 {angle:.2f}° - 已校正")
            
            return result
            
        except Exception as e:
            result['message'] = f'處理失敗: {str(e)}'
            if verbose:
                print(f"✗ {input_path.name}: {str(e)}")
            return result
            
    def correct_batch(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        inplace: bool = False,
        verbose: bool = True
    ) -> Tuple[int, int, List[Dict]]:
        """
        批次校正圖片
        
        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄（如果 inplace=False）
            inplace: 是否覆蓋原圖
            verbose: 是否顯示進度
            
        Returns:
            (成功數量, 總數量, 結果列表)
        """
        # 找出所有圖片檔案
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(input_dir.glob(ext))
        
        image_files = sorted(image_files)
        total = len(image_files)
        
        if total == 0:
            return 0, 0, []
        
        if verbose:
            print(f"\n開始批次處理 {total} 張圖片...")
            print(f"輸入目錄: {input_dir}")
            if not inplace:
                print(f"輸出目錄: {output_dir}")
            print(f"跳過閾值: ±{self.skip_threshold}°\n")
        
        results = []
        success_count = 0
        
        for i, img_path in enumerate(image_files, 1):
            if verbose:
                print(f"[{i}/{total}] 處理: {img_path.name}")
            
            # 計算輸出路徑
            if not inplace and output_dir:
                output_path = output_dir / img_path.name
            else:
                output_path = None
            
            # 處理單張圖片
            result = self.correct_single(
                img_path,
                output_path,
                inplace=inplace,
                verbose=False  # 這裡設為 False，由外層控制輸出
            )
            
            results.append(result)
            
            if result['success']:
                success_count += 1
                angle_info = f"{result['angle']:.2f}°" if result['angle'] is not None else "N/A"
                if result.get('skipped', False):
                    if verbose:
                        print(f"  ⊙ 角度: {angle_info} - 跳過校正")
                else:
                    if verbose:
                        print(f"  ✓ 角度: {angle_info} - 已校正")
            else:
                if verbose:
                    print(f"  ✗ {result['message']}")
        
        if verbose:
            print(f"\n批次處理完成:")
            print(f"  - 成功: {success_count}/{total}")
            print(f"  - 失敗: {total - success_count}/{total}")
        
        return success_count, total, results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="基於 deskew 的圖片旋轉校正工具")
    parser.add_argument("input", help="輸入圖片或目錄路徑")
    parser.add_argument("-o", "--output", help="輸出圖片或目錄路徑")
    parser.add_argument("-i", "--inplace", action="store_true", help="覆蓋原圖")
    parser.add_argument("-t", "--threshold", type=float, default=5.0, 
                       help="跳過校正的角度閾值（度）")
    parser.add_argument("-s", "--sigma", type=float, default=3.0,
                       help="高斯模糊的 sigma 值")
    parser.add_argument("-p", "--peaks", type=int, default=20,
                       help="Hough transform 的峰值數量")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細信息")
    
    args = parser.parse_args()
    
    # 創建校正器
    corrector = RotationCorrectorDeskew(
        skip_threshold=args.threshold,
        sigma=args.sigma,
        num_peaks=args.peaks
    )
    
    input_path = Path(args.input)
    
    # 處理單張圖片或批次處理
    if input_path.is_file():
        output_path = Path(args.output) if args.output else None
        result = corrector.correct_single(
            input_path,
            output_path,
            inplace=args.inplace,
            verbose=True
        )
        
        if result['success']:
            print(f"\n✓ 處理成功")
        else:
            print(f"\n✗ 處理失敗: {result['message']}")
            sys.exit(1)
            
    elif input_path.is_dir():
        output_dir = Path(args.output) if args.output else None
        success, total, results = corrector.correct_batch(
            input_path,
            output_dir,
            inplace=args.inplace,
            verbose=args.verbose
        )
        
        if success < total:
            sys.exit(1)
    else:
        print(f"錯誤: 路徑不存在 - {input_path}")
        sys.exit(1)
