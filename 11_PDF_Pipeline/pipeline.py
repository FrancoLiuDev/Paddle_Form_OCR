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

# 加入 tools 模組路徑
sys.path.insert(0, str(Path(__file__).parent))
from tools import PDFConverter


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
        
        print(f"✓ 載入配置: {self.config['pipeline_name']} v{self.config['version']}")
        
    def run(self):
        """執行 Pipeline"""
        print(f"\n{'='*60}")
        print(f"開始執行 Pipeline: {self.config['pipeline_name']}")
        print(f"{'='*60}\n")
        
        results = []
        
        for step_config in self.config['steps']:
            if not step_config.get('enabled', True):
                print(f"⊘ 跳過已停用的步驟: {step_config['name']}")
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
            else:
                logger.warning(f"未實作的步驟: {step_id}")
                continue
            
            # 執行
            result = step.execute()
            results.append(result)
            
            # 如果失敗，停止後續步驟
            if result['status'] == 'failed':
                print(f"\n✗ Pipeline 因步驟失敗而中止")
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
        
        print(f"\n✓ 結果已儲存: {result_file}")


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
        print(f"\n✗ Pipeline 執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
