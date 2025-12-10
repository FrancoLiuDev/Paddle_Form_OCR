"""
PDF 轉圖片工具模組
封裝 PDF 到圖片的轉換功能
"""

from pathlib import Path
import sys
import subprocess


class PDFConverter:
    """PDF 轉圖片轉換器"""
    
    def __init__(self, dpi=300, image_format="PNG"):
        """初始化轉換器
        
        Args:
            dpi: 解析度，預設 300
            image_format: 圖片格式，預設 PNG
        """
        self.dpi = dpi
        self.image_format = image_format.upper()
        self.script_path = Path(__file__).parent / "pdf_to_images.py"
        
        if not self.script_path.exists():
            raise FileNotFoundError(f"找不到轉換腳本: {self.script_path}")
    
    def convert(self, pdf_path, output_dir):
        """轉換 PDF 為圖片
        
        Args:
            pdf_path: PDF 檔案路徑
            output_dir: 輸出目錄
            
        Returns:
            tuple: (success, message, output_files)
        """
        pdf_path = Path(pdf_path).absolute()
        output_dir = Path(output_dir).absolute()
        
        if not pdf_path.exists():
            return False, f"PDF 檔案不存在: {pdf_path}", []
        
        # 確保輸出目錄存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 執行轉換
        cmd = [
            sys.executable,
            str(self.script_path),
            str(pdf_path),
            "--dpi", str(self.dpi),
            "--format", self.image_format,
            "--output", str(output_dir)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5分鐘超時
            )
            
            # 即使 returncode 為 0，也檢查是否有實際輸出
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                return False, f"轉換失敗: {error_msg}", []
            
            # 收集輸出的圖片檔案
            output_files = sorted(list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg")))
            
            if len(output_files) == 0:
                return False, "轉換完成但未產生圖片檔案", []
            
            return True, f"成功轉換 {len(output_files)} 張圖片", output_files
            
        except subprocess.TimeoutExpired:
            return False, "轉換超時（超過 5 分鐘）", []
        except Exception as e:
            return False, f"執行錯誤: {str(e)}", []


__all__ = ['PDFConverter']
