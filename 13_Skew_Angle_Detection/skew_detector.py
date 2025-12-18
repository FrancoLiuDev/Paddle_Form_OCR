"""
Skew Angle Detection Module
使用 deskew 套件檢測圖片的傾斜角度
"""

import cv2
import numpy as np
from deskew import determine_skew
from typing import Optional, Tuple
from pathlib import Path


class SkewDetector:
    """傾斜角度檢測器"""
    
    def __init__(
        self,
        sigma: float = 3.0,
        num_peaks: int = 20,
        min_angle: Optional[float] = None,
        max_angle: Optional[float] = None,
        min_deviation: float = 1.0
    ):
        """
        初始化傾斜角度檢測器
        
        Parameters
        ----------
        sigma : float
            Canny 邊緣檢測的標準差，預設 3.0
        num_peaks : int
            要檢測的峰值數量，預設 20
        min_angle : float, optional
            最小角度限制（度）
        max_angle : float, optional
            最大角度限制（度）
        min_deviation : float
            角度解析度（度），預設 1.0
        """
        self.sigma = sigma
        self.num_peaks = num_peaks
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_deviation = min_deviation
    
    def detect_angle(
        self,
        image: np.ndarray,
        grayscale: bool = False
    ) -> Optional[float]:
        """
        檢測圖片的傾斜角度
        
        Parameters
        ----------
        image : np.ndarray
            輸入圖片（BGR 或灰階）
        grayscale : bool
            圖片是否已經是灰階，預設 False
        
        Returns
        -------
        float or None
            傾斜角度（度），如果無法檢測則回傳 None
        """
        # 確保圖片是灰階
        if not grayscale and len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 使用 deskew 檢測角度
        angle = determine_skew(
            gray,
            sigma=self.sigma,
            num_peaks=self.num_peaks,
            min_angle=self.min_angle,
            max_angle=self.max_angle,
            min_deviation=self.min_deviation
        )
        
        return angle
    
    def detect_angle_from_file(
        self,
        image_path: str
    ) -> Optional[float]:
        """
        從檔案路徑檢測圖片的傾斜角度
        
        Parameters
        ----------
        image_path : str
            圖片檔案路徑
        
        Returns
        -------
        float or None
            傾斜角度（度），如果無法檢測則回傳 None
        """
        # 檢查檔案是否存在
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"圖片檔案不存在: {image_path}")
        
        # 讀取圖片（灰階）
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        
        if image is None:
            raise ValueError(f"無法讀取圖片: {image_path}")
        
        # 檢測角度
        return self.detect_angle(image, grayscale=True)
    
    def detect_batch(
        self,
        image_paths: list,
        verbose: bool = False
    ) -> dict:
        """
        批次檢測多張圖片的傾斜角度
        
        Parameters
        ----------
        image_paths : list
            圖片檔案路徑列表
        verbose : bool
            是否顯示詳細資訊
        
        Returns
        -------
        dict
            檔案名稱到角度的映射字典
        """
        results = {}
        
        for image_path in image_paths:
            try:
                angle = self.detect_angle_from_file(image_path)
                results[Path(image_path).name] = angle
                
                if verbose:
                    if angle is not None:
                        print(f"{Path(image_path).name}: {angle:.2f}°")
                    else:
                        print(f"{Path(image_path).name}: 無法檢測")
                        
            except Exception as e:
                results[Path(image_path).name] = None
                if verbose:
                    print(f"{Path(image_path).name}: 錯誤 - {e}")
        
        return results


def detect_skew_angle(
    image_path: str,
    sigma: float = 3.0,
    num_peaks: int = 20,
    min_angle: Optional[float] = None,
    max_angle: Optional[float] = None,
    min_deviation: float = 1.0
) -> Optional[float]:
    """
    簡單的函數介面：檢測圖片的傾斜角度
    
    Parameters
    ----------
    image_path : str
        圖片檔案路徑
    sigma : float
        Canny 邊緣檢測的標準差
    num_peaks : int
        要檢測的峰值數量
    min_angle : float, optional
        最小角度限制（度）
    max_angle : float, optional
        最大角度限制（度）
    min_deviation : float
        角度解析度（度）
    
    Returns
    -------
    float or None
        傾斜角度（度），如果無法檢測則回傳 None
    
    Examples
    --------
    >>> angle = detect_skew_angle('document.png')
    >>> print(f"Detected angle: {angle}°")
    """
    detector = SkewDetector(
        sigma=sigma,
        num_peaks=num_peaks,
        min_angle=min_angle,
        max_angle=max_angle,
        min_deviation=min_deviation
    )
    
    return detector.detect_angle_from_file(image_path)


if __name__ == "__main__":
    # 測試範例
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        angle = detect_skew_angle(image_path)
        
        if angle is not None:
            print(f"檢測到的傾斜角度: {angle:.2f}°")
        else:
            print("無法檢測到傾斜角度")
    else:
        print("使用方法: python skew_detector.py <image_path>")
