#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高品質 PDF 轉圖片工具
支援最佳化設定，保持最高品質
"""

import os
import sys
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ 請先安裝 PyMuPDF: pip install PyMuPDF")
    sys.exit(1)

from PIL import Image
import io


class PDFToImages:
    """PDF 轉圖片處理器"""
    
    def __init__(self, output_dir: str = "output", dpi: int = 300, image_format: str = "PNG"):
        """初始化
        
        Args:
            output_dir: 輸出目錄
            dpi: 解析度 (DPI)，預設 300，越高品質越好
            image_format: 圖片格式 (PNG/JPG)，PNG 為無損格式
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.image_format = image_format.upper()
        
        # DPI 轉換為縮放倍數 (72 DPI 是 PDF 的基準)
        self.zoom = dpi / 72.0
        
    def convert_pdf(self, pdf_path: str) -> list:
        """轉換 PDF 為圖片
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            生成的圖片路徑列表
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"找不到 PDF 檔案: {pdf_path}")
        
        print(f"\n📄 正在處理: {pdf_path.name}")
        print(f"   設定: {self.dpi} DPI, 格式: {self.image_format}")
        print(f"   縮放倍數: {self.zoom:.2f}x")
        
        # 開啟 PDF
        pdf_document = fitz.open(str(pdf_path))
        total_pages = len(pdf_document)
        print(f"   總頁數: {total_pages}")
        
        # 直接使用輸出目錄，不建立子目錄
        image_paths = []
        
        # 轉換每一頁
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            
            # 設定轉換矩陣 (高品質)
            mat = fitz.Matrix(self.zoom, self.zoom)
            
            # 轉換為圖片 (最高品質設定)
            pix = page.get_pixmap(
                matrix=mat,
                alpha=False,  # 不要透明通道，減少檔案大小
                colorspace=fitz.csRGB  # RGB 色彩空間
            )
            
            # 輸出檔名（直接在輸出目錄）
            page_number = page_num + 1
            if self.image_format == "PNG":
                output_file = self.output_dir / f"page_{page_number:03d}.png"
            else:
                output_file = self.output_dir / f"page_{page_number:03d}.jpg"
            
            # 使用 PIL 進行最佳化保存
            img_data = pix.tobytes("png" if self.image_format == "PNG" else "jpeg")
            img = Image.open(io.BytesIO(img_data))
            
            if self.image_format == "PNG":
                # PNG 無損壓縮，最高品質
                img.save(
                    output_file,
                    "PNG",
                    optimize=True,  # 優化壓縮
                    compress_level=6  # 壓縮等級 (0-9，6 是平衡點)
                )
            else:
                # JPEG 高品質壓縮
                img.save(
                    output_file,
                    "JPEG",
                    quality=95,  # 品質 95%
                    optimize=True,  # 優化壓縮
                    subsampling=0  # 不要色度二次抽樣 (最高品質)
                )
            
            file_size = output_file.stat().st_size / 1024  # KB
            print(f"   ✅ 第 {page_number}/{total_pages} 頁: {output_file.name} ({file_size:.1f} KB)")
            
            image_paths.append(str(output_file))
        
        pdf_document.close()
        
        # 統計資訊
        total_size = sum(Path(p).stat().st_size for p in image_paths)
        avg_size = total_size / len(image_paths) if image_paths else 0
        
        print(f"\n✨ 完成！")
        print(f"   輸出目錄: {self.output_dir}")
        print(f"   圖片數量: {len(image_paths)}")
        print(f"   總大小: {total_size / 1024 / 1024:.2f} MB")
        print(f"   平均大小: {avg_size / 1024:.2f} KB/頁")
        
        return image_paths


def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="高品質 PDF 轉圖片工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 使用預設設定 (300 DPI, PNG)
  python pdf_to_images.py input/013大安.pdf
  
  # 指定更高解析度
  python pdf_to_images.py input/013大安.pdf --dpi 600
  
  # 使用 JPEG 格式 (檔案較小)
  python pdf_to_images.py input/013大安.pdf --format JPG
  
  # 自訂輸出目錄
  python pdf_to_images.py input/013大安.pdf --output my_output
        """
    )
    
    parser.add_argument(
        "pdf_file",
        help="PDF 檔案路徑"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="解析度 (DPI)，預設 300。建議值: 150(快速), 300(標準), 600(高品質)"
    )
    parser.add_argument(
        "--format",
        choices=["PNG", "JPG", "JPEG"],
        default="PNG",
        help="圖片格式，預設 PNG (無損)"
    )
    parser.add_argument(
        "--output",
        default="output",
        help="輸出目錄，預設 'output'"
    )
    
    args = parser.parse_args()
    
    # 正規化格式名稱
    image_format = "PNG" if args.format == "PNG" else "JPG"
    
    try:
        converter = PDFToImages(
            output_dir=args.output,
            dpi=args.dpi,
            image_format=image_format
        )
        converter.convert_pdf(args.pdf_file)
        
    except FileNotFoundError as e:
        print(f"\n❌ 錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 處理失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
