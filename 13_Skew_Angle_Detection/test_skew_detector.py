"""
測試腳本：檢測圖片傾斜角度
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from skew_detector import SkewDetector, detect_skew_angle

# 測試單張圖片
def test_single_image():
    """測試單張圖片"""
    print("=" * 60)
    print("測試單張圖片")
    print("=" * 60)
    
    # 使用簡單函數
    image_path = '../images/fuji45.png'
    angle = detect_skew_angle(image_path)
    
    if angle is not None:
        print(f"圖片: {image_path}")
        print(f"傾斜角度: {angle:.2f}°")
    else:
        print("無法檢測到傾斜角度")
    print()


def test_detector_class():
    """測試檢測器類別"""
    print("=" * 60)
    print("測試檢測器類別")
    print("=" * 60)
    
    # 創建檢測器實例
    detector = SkewDetector(
        sigma=3.0,
        num_peaks=20,
        min_angle=-45,
        max_angle=45
    )
    
    # 測試多張圖片
    test_images = [
        '../images/fuji45.png',
        '../images/fuji3.png',
        '../images/page_014.png',
    ]
    
    for img_path in test_images:
        if os.path.exists(img_path):
            try:
                angle = detector.detect_angle_from_file(img_path)
                if angle is not None:
                    print(f"✓ {os.path.basename(img_path)}: {angle:.2f}°")
                else:
                    print(f"✗ {os.path.basename(img_path)}: 無法檢測")
            except Exception as e:
                print(f"✗ {os.path.basename(img_path)}: 錯誤 - {e}")
        else:
            print(f"✗ {os.path.basename(img_path)}: 檔案不存在")
    print()


def test_batch_detection():
    """測試批次檢測"""
    print("=" * 60)
    print("測試批次檢測")
    print("=" * 60)
    
    detector = SkewDetector()
    
    # 準備圖片列表
    image_dir = '../images'
    if os.path.exists(image_dir):
        image_files = [
            os.path.join(image_dir, f) 
            for f in os.listdir(image_dir) 
            if f.endswith(('.png', '.jpg', '.jpeg'))
        ][:5]  # 只測試前 5 張
        
        if image_files:
            print(f"批次檢測 {len(image_files)} 張圖片:\n")
            results = detector.detect_batch(image_files, verbose=True)
            
            print(f"\n檢測結果摘要:")
            print(f"- 成功檢測: {sum(1 for v in results.values() if v is not None)} 張")
            print(f"- 無法檢測: {sum(1 for v in results.values() if v is None)} 張")
        else:
            print("找不到測試圖片")
    else:
        print(f"圖片目錄不存在: {image_dir}")
    print()


def test_with_parameters():
    """測試不同參數設定"""
    print("=" * 60)
    print("測試不同參數設定")
    print("=" * 60)
    
    image_path = '../images/page_014.png'
    
    if not os.path.exists(image_path):
        print(f"測試圖片不存在: {image_path}")
        return
    
    # 測試不同的 sigma 值
    print("測試不同的 sigma 值:")
    for sigma in [1.0, 3.0, 5.0]:
        detector = SkewDetector(sigma=sigma)
        angle = detector.detect_angle_from_file(image_path)
        if angle is not None:
            print(f"  sigma={sigma}: {angle:.2f}°")
        else:
            print(f"  sigma={sigma}: 無法檢測")
    
    print()
    
    # 測試不同的 num_peaks 值
    print("測試不同的 num_peaks 值:")
    for num_peaks in [10, 20, 40]:
        detector = SkewDetector(num_peaks=num_peaks)
        angle = detector.detect_angle_from_file(image_path)
        if angle is not None:
            print(f"  num_peaks={num_peaks}: {angle:.2f}°")
        else:
            print(f"  num_peaks={num_peaks}: 無法檢測")
    
    print()


if __name__ == "__main__":
    print("\n🔍 Skew Angle Detection 測試\n")
    
    # 執行所有測試
    test_single_image()
    test_detector_class()
    test_batch_detection()
    test_with_parameters()
    
    print("=" * 60)
    print("測試完成")
    print("=" * 60)
