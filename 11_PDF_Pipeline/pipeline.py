#!/usr/bin/env python3
"""
PDF Processing Pipeline
執行步驟化的 PDF 處理流程
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import random
import cv2

# 加入 tools 模組路徑（必須在最前面，避免與 PaddleOCR 的 tools 衝突）
_SCRIPT_DIR = Path(__file__).parent
_TOOLS_DIR = _SCRIPT_DIR / "tools"
sys.path.insert(0, str(_SCRIPT_DIR))

# 從本地 tools 模組導入
from tools.pdf_converter import PDFConverter
from tools.rotation_corrector import RotationCorrector
from tools.ocr_recognizer import OCRRecognizer


class PipelineLogger:
    """Pipeline 日誌管理"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_step_logger(self, step_id, log_file):
        """設置步驟日誌"""
        logger = logging.getLogger(f"pipeline.{step_id}")
        logger.setLevel(logging.INFO)
        
        # 清除現有的 handlers
        logger.handlers.clear()
        
        # 檔案 handler (log_file 已經包含 logs/ 路徑)
        log_path = Path(log_file)
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger


class Step1_PDFToImages:
    """Step 1: PDF 轉圖片"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.step_id = config['step_id']
        self.name = config['name']
        
    def validate_input(self):
        """驗證輸入"""
        input_dir = Path(self.config['input']['source'])
        
        if not input_dir.exists():
            raise FileNotFoundError(f"輸入目錄不存在: {input_dir}")
        
        # 檢查是否只有一個 PDF
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if len(pdf_files) == 0:
            raise FileNotFoundError(f"在 {input_dir} 中找不到 PDF 檔案")
        
        if len(pdf_files) > 1:
            raise ValueError(f"輸入目錄只能有一個 PDF 檔案，目前有 {len(pdf_files)} 個")
        
        self.input_file = pdf_files[0]
        self.logger.info(f"✓ 輸入驗證通過: {self.input_file.name}")
        return True
        
    def execute(self):
        """執行步驟"""
        start_time = datetime.now()
        
        try:
            # 驗證輸入
            self.validate_input()
            
            # 準備輸出目錄
            output_dir = Path(self.config['output']['destination'])
            if output_dir.exists():
                self.logger.info(f"清空輸出目錄: {output_dir}")
                shutil.rmtree(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 執行 PDF 轉圖片
            self.logger.info(f"開始執行: {self.name}")
            self.logger.info(f"輸入檔案: {self.input_file}")
            self.logger.info(f"輸出目錄: {output_dir}")
            
            # 使用內建的 PDFConverter 工具
            params = self.config['processing']['parameters']
            converter = PDFConverter(
                dpi=params.get('dpi', 300),
                image_format=params.get('format', 'PNG')
            )
            
            self.logger.info(f"使用 DPI: {converter.dpi}, 格式: {converter.image_format}")
            
            # 執行轉換
            success, message, output_files = converter.convert(
                str(self.input_file.absolute()),
                str(output_dir.absolute())
            )
            
            if not success:
                self.logger.error(f"轉換失敗: {message}")
                raise RuntimeError(f"PDF 轉換失敗: {message}")
            
            self.logger.info(message)
            # 如果配置啟用，對每張轉出的圖片施加隨機旋轉（預設啟用）
            try:
                rotate_after = params.get('random_rotate_after_split', True)
                max_deg = float(params.get('random_rotate_max_deg', 11.0))
            except Exception:
                rotate_after = True
                max_deg = 11.0

            if rotate_after:
                self.logger.info(f"對每張輸出圖片應用隨機旋轉 ±{max_deg}°")
                for f in output_files:
                    try:
                        img = cv2.imread(str(f))
                        if img is None:
                            self.logger.warning(f"讀取圖片失敗，略過: {f}")
                            continue
                        h, w = img.shape[:2]
                        angle = random.uniform(-max_deg, max_deg)
                        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
                        rotated = cv2.warpAffine(
                            img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255)
                        )
                        cv2.imwrite(str(f), rotated)
                        self.logger.info(f"  {f.name} -> rotated {angle:.2f}°")
                    except Exception as e:
                        self.logger.warning(f"旋轉圖片失敗: {f} - {e}")
            
            # 統計輸出
            total_size = sum(f.stat().st_size for f in output_files)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 記錄結果
            result_data = {
                "step_id": self.step_id,
                "name": self.name,
                "status": "success",
                "timestamp": start_time.isoformat(),
                "input": {
                    "file": str(self.input_file),
                    "size": self.input_file.stat().st_size
                },
                "processing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                },
                "output": {
                    "directory": str(output_dir),
                    "files_created": len(output_files),
                    "total_size": total_size,
                    "files": [f.name for f in sorted(output_files)]
                }
            }
            
            self.logger.info(f"✓ 步驟完成")
            self.logger.info(f"  - 產生圖片: {len(output_files)} 張")
            self.logger.info(f"  - 總大小: {total_size / 1024 / 1024:.2f} MB")
            self.logger.info(f"  - 執行時間: {duration:.2f} 秒")
            
            return result_data
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.error(f"✗ 步驟失敗: {str(e)}")
            
            result_data = {
                "step_id": self.step_id,
                "name": self.name,
                "status": "failed",
                "timestamp": start_time.isoformat(),
                "processing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                },
                "error": str(e)
            }
            
            return result_data


class Step2_RotationCorrection:
    """Step 2: 圖片角度校正"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.step_id = config['step_id']
        self.name = config['name']
        
    def validate_input(self):
        """驗證輸入"""
        input_dir = Path(self.config['input']['source'])
        
        if not input_dir.exists():
            raise FileNotFoundError(f"輸入目錄不存在: {input_dir}")
        
        # 檢查是否有圖片檔案
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(input_dir.glob(ext))
        
        if len(image_files) == 0:
            raise FileNotFoundError(f"在 {input_dir} 中找不到圖片檔案")
        
        self.input_dir = input_dir
        self.image_files = sorted(image_files)
        self.logger.info(f"✓ 輸入驗證通過: 找到 {len(self.image_files)} 張圖片")
        return True
        
    def execute(self):
        """執行步驟"""
        start_time = datetime.now()
        
        try:
            # 驗證輸入
            self.validate_input()
            
            # 執行角度校正
            self.logger.info(f"開始執行: {self.name}")
            self.logger.info(f"輸入目錄: {self.input_dir}")
            self.logger.info(f"圖片數量: {len(self.image_files)}")
            
            # 使用 RotationCorrector 工具
            params = self.config['processing']['parameters']
            corrector = RotationCorrector(
                degree=params.get('degree', 30),
                skip_threshold=params.get('skip_threshold', 5.0)
            )
            
            self.logger.info(f"使用角度範圍: ±{corrector.degree}°")
            self.logger.info(f"跳過閾值: ±{corrector.skip_threshold}°")
            self.logger.info(f"處理模式: {'覆蓋原圖' if params.get('inplace', False) else '另存新檔'}")
            
            # 批次執行校正
            output_dir = Path(self.config['output']['destination'])
            success_count, total_count, results = corrector.correct_batch(
                self.input_dir,
                output_dir if not params.get('inplace', False) else None,
                inplace=params.get('inplace', False),
                verbose=False
            )
            
            # 記錄每個檔案的處理結果
            skipped_count = 0
            rotated_count = 0
            
            for result in results:
                if result['success']:
                    angle_info = f" (角度: {result['angle']:.2f}°)" if result['angle'] is not None else ""
                    if result.get('skipped', False):
                        self.logger.info(f"  ⊙ {result['file']}{angle_info} - 跳過旋轉")
                        skipped_count += 1
                    else:
                        self.logger.info(f"  ✓ {result['file']}{angle_info} - 已旋轉")
                        rotated_count += 1
                else:
                    self.logger.warning(f"  ✗ {result['file']}: {result['message']}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 記錄結果
            result_data = {
                "step_id": self.step_id,
                "name": self.name,
                "status": "success" if success_count == total_count else "partial_success",
                "timestamp": start_time.isoformat(),
                "input": {
                    "directory": str(self.input_dir),
                    "files_count": total_count
                },
                "processing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "success_count": success_count,
                    "failed_count": total_count - success_count,
                    "rotated_count": rotated_count,
                    "skipped_count": skipped_count,
                    "skip_threshold": corrector.skip_threshold
                },
                "output": {
                    "directory": str(output_dir),
                    "mode": "inplace" if params.get('inplace', False) else "new_files"
                },
                "details": results
            }
            
            self.logger.info(f"✓ 步驟完成")
            self.logger.info(f"  - 處理成功: {success_count}/{total_count} 張")
            self.logger.info(f"  - 已旋轉: {rotated_count} 張")
            self.logger.info(f"  - 跳過旋轉: {skipped_count} 張 (角度在 ±{corrector.skip_threshold}° 內)")
            self.logger.info(f"  - 執行時間: {duration:.2f} 秒")
            
            if success_count < total_count:
                self.logger.warning(f"  ! 有 {total_count - success_count} 張圖片處理失敗")
            
            return result_data
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.error(f"✗ 步驟失敗: {str(e)}")
            
            result_data = {
                "step_id": self.step_id,
                "name": self.name,
                "status": "failed",
                "timestamp": start_time.isoformat(),
                "processing": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                },
                "error": str(e)
            }
            
            return result_data


class Step3_OCRRecognition:
    """步驟 3: OCR 文字識別"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.step_id = config['step_id']
        self.step_name = config['name']
        
        # 取得配置
        self.input_config = config.get('input', {})
        self.output_config = config.get('output', {})
        self.processing_config = config.get('processing', {})
        
        # 路徑
        self.input_dir = Path(self.input_config.get('source', 'meta/images_rotated'))
        self.output_dir = Path(self.output_config.get('destination', 'meta/ocr'))
        
        # 處理參數
        params = self.processing_config.get('parameters', {})
        self.lang = params.get('lang', 'ch')
        self.use_gpu = params.get('use_gpu', False)
        self.high_sensitivity = params.get('high_sensitivity', False)
        self.convert_fullwidth = params.get('convert_fullwidth', True)
    
    def validate_input(self):
        """驗證輸入"""
        if not self.input_dir.exists():
            raise ValueError(f"輸入目錄不存在: {self.input_dir}")
        
        # 檢查是否有圖片
        image_files = list(self.input_dir.glob("*.png")) + list(self.input_dir.glob("*.jpg"))
        if not image_files:
            raise ValueError(f"輸入目錄沒有圖片: {self.input_dir}")
        
        self.logger.info(f"✓ 輸入驗證通過: 找到 {len(image_files)} 張圖片")
        return True
    
    def execute(self):
        """執行 OCR 識別"""
        result_data = {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "status": "unknown",
            "input": {},
            "output": {},
            "processing": {}
        }
        
        try:
            start_time = datetime.now()
            
            # 驗證輸入
            self.validate_input()
            
            # 記錄開始
            self.logger.info(f"開始執行: {self.step_name}")
            self.logger.info(f"輸入目錄: {self.input_dir}")
            self.logger.info(f"輸出目錄: {self.output_dir}")
            self.logger.info(f"語言: {self.lang}, GPU: {self.use_gpu}")
            self.logger.info(f"高敏感度: {self.high_sensitivity}, 全形轉換: {self.convert_fullwidth}")
            
            # 建立 OCR 識別器
            recognizer = OCRRecognizer(
                lang=self.lang,
                use_gpu=self.use_gpu,
                high_sensitivity=self.high_sensitivity,
                convert_fullwidth=self.convert_fullwidth,
                verbose=False  # 使用 logger 而非 print
            )
            
            # 批次處理
            success_count, total_count, results = recognizer.recognize_batch(
                input_dir=self.input_dir,
                output_dir=self.output_dir
            )
            
            # 記錄每個檔案的結果
            for result in results:
                if result['success']:
                    self.logger.info(f"  ✓ {result['file']} → {result['output']} ({result['blocks']} 個文字塊)")
                else:
                    self.logger.warning(f"  ✗ {result['file']}: {result['message']}")
            
            # 計算統計
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 計算總文字塊數
            total_blocks = sum(r['blocks'] for r in results)
            
            # 記錄完成
            self.logger.info(f"✓ 步驟完成")
            self.logger.info(f"  - 處理成功: {success_count}/{total_count} 張")
            self.logger.info(f"  - 總文字塊: {total_blocks} 個")
            self.logger.info(f"  - 執行時間: {duration:.2f} 秒")
            
            # 組織結果資料
            result_data.update({
                "status": "success" if success_count == total_count else "partial",
                "input": {
                    "source": str(self.input_dir),
                    "total_images": total_count
                },
                "output": {
                    "destination": str(self.output_dir),
                    "json_files": success_count,
                    "format": "JSON"
                },
                "processing": {
                    "tool": "ocr_recognizer",
                    "parameters": {
                        "lang": self.lang,
                        "use_gpu": self.use_gpu,
                        "high_sensitivity": self.high_sensitivity,
                        "convert_fullwidth": self.convert_fullwidth
                    },
                    "success_count": success_count,
                    "total_count": total_count,
                    "total_text_blocks": total_blocks,
                    "results": results,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration
                }
            })
            
            return result_data
            
        except Exception as e:
            self.logger.error(f"✗ 步驟失敗: {str(e)}")
            
            result_data.update({
                "status": "failed",
                "processing": {
                    "start_time": start_time.isoformat() if 'start_time' in locals() else None,
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
                },
                "error": str(e)
            })
            
            return result_data


class Pipeline:
    """主 Pipeline 類別"""
    
    def __init__(self, config_file="pipeline_config.json"):
        self.config_file = Path(config_file)
        self.load_config()
        self.logger_manager = PipelineLogger()
        
    def load_config(self):
        """載入配置"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"找不到配置檔案: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        print(f"載入配置: {self.config['pipeline_name']} v{self.config['version']}")
        
    def run(self):
        """執行 Pipeline"""
        print(f"\n{'='*60}")
        print(f"開始執行 Pipeline: {self.config['pipeline_name']}")
        print(f"{'='*60}\n")
        
        results = []
        
        for step_config in self.config['steps']:
            if not step_config.get('enabled', True):
                print(f"跳過已停用的步驟: {step_config['name']}")
                continue
            
            step_id = step_config['step_id']
            
            print(f"\n{'─'*60}")
            print(f"執行步驟: {step_config['name']} ({step_id})")
            print(f"{'─'*60}\n")
            
            # 設置日誌
            logger = self.logger_manager.setup_step_logger(
                step_id,
                step_config['log']['file']
            )
            
            # 執行對應的步驟
            if step_id == "step1":
                step = Step1_PDFToImages(step_config, logger)
            elif step_id == "step2":
                step = Step2_RotationCorrection(step_config, logger)
            elif step_id == "step3":
                step = Step3_OCRRecognition(step_config, logger)
            else:
                logger.warning(f"未實作的步驟: {step_id}")
                continue
            
            # 執行
            result = step.execute()
            results.append(result)
            
            # 如果失敗，停止後續步驟
            if result['status'] == 'failed':
                print(f"\nPipeline 因步驟失敗而中止")
                break
        
        # 儲存整體結果
        self.save_results(results)
        
        print(f"\n{'='*60}")
        print(f"Pipeline 執行完成")
        print(f"{'='*60}\n")
        
        return results
        
    def save_results(self, results):
        """儲存執行結果"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        result_file = output_dir / f"pipeline_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "pipeline": self.config['pipeline_name'],
                "version": self.config['version'],
                "execution_time": datetime.now().isoformat(),
                "steps": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果已儲存: {result_file}")


def main():
    """主程式"""
    try:
        pipeline = Pipeline()
        results = pipeline.run()
        
        # 檢查是否全部成功
        all_success = all(r['status'] == 'success' for r in results)
        
        if all_success:
            print("\n✓ 所有步驟執行成功！")
            return 0
        else:
            print("\n✗ 部分步驟執行失敗")
            return 1
            
    except Exception as e:
        print(f"\nPipeline 執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
