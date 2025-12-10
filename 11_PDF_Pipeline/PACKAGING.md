# 打包為執行檔指南

## 🎯 目標

將 `11_PDF_Pipeline` 打包成單一執行檔，方便在其他電腦上使用，不需要安裝 Python 環境。

## 📋 方案比較

### 方案 1: PyInstaller（推薦）

**優點**：
- ✅ 打包成單一執行檔
- ✅ 支援 Linux/Windows/macOS
- ✅ 使用簡單

**缺點**：
- ⚠️ 檔案較大（~50-100MB）
- ⚠️ 啟動速度較慢

### 方案 2: Python + venv（輕量）

**優點**：
- ✅ 檔案較小
- ✅ 啟動速度快
- ✅ 易於更新

**缺點**：
- ⚠️ 需要 Python 環境

### 方案 3: Docker 容器（最佳隔離）

**優點**：
- ✅ 完全隔離環境
- ✅ 可跨平台
- ✅ 易於部署

**缺點**：
- ⚠️ 需要 Docker
- ⚠️ 較複雜

## 🚀 方案 1: PyInstaller 打包

### 1. 安裝 PyInstaller

```bash
pip3 install pyinstaller
```

### 2. 執行打包

```bash
./build_executable.sh
```

或手動打包：

```bash
pyinstaller --onefile \
    --name pdf_pipeline \
    --add-data "pipeline_config.json:." \
    --add-data "tools:tools" \
    pipeline.py
```

### 3. 使用執行檔

打包完成後，執行檔位於 `dist/pdf_pipeline`：

```bash
# 複製到目標位置
cp dist/pdf_pipeline /path/to/target/

# 準備目錄結構
cd /path/to/target/
mkdir -p input output logs meta

# 放入 PDF
cp your.pdf input/

# 執行
./pdf_pipeline
```

## 🐳 方案 2: Docker 容器

### 1. 建立 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案
COPY . .

# 建立目錄
RUN mkdir -p input output logs meta

# 執行
CMD ["python3", "pipeline.py"]
```

### 2. 建立映像

```bash
docker build -t pdf-pipeline .
```

### 3. 執行容器

```bash
docker run -v $(pwd)/input:/app/input \
           -v $(pwd)/output:/app/output \
           pdf-pipeline
```

## 📦 方案 3: Portable Python 包

### 1. 建立 setup.py

```python
from setuptools import setup, find_packages

setup(
    name="pdf_pipeline",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF>=1.23.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        'console_scripts': [
            'pdf-pipeline=pipeline:main',
        ],
    },
)
```

### 2. 安裝

```bash
pip install .
```

### 3. 使用

```bash
pdf-pipeline
```

## 🎨 推薦方案

### 給一般用戶：**PyInstaller**
- 簡單易用
- 不需要 Python 環境
- 執行 `./build_executable.sh` 即可

### 給開發者：**Portable Package**
- 易於維護
- 可快速更新
- 使用 `pip install .`

### 給伺服器部署：**Docker**
- 環境隔離
- 易於擴展
- CI/CD 友善

## 📝 目前狀態

✅ **專案已模組化**
- 所有工具已打包到 `tools/` 目錄
- 不依賴外部 `8_PDF_To_Images`
- 可獨立運作

✅ **可直接打包**
- 執行 `./build_executable.sh` 即可打包
- 生成的執行檔在 `dist/pdf_pipeline`

## 🔧 測試打包結果

```bash
# 打包
./build_executable.sh

# 測試執行檔
mkdir -p test_deploy
cp dist/pdf_pipeline test_deploy/
cd test_deploy/
mkdir -p input output logs meta
cp /path/to/test.pdf input/
./pdf_pipeline
```

## 💡 最佳實踐

1. **版本管理**：在 `pipeline_config.json` 中維護版本號
2. **錯誤處理**：完整的日誌記錄在 `logs/` 目錄
3. **文檔完整**：包含 README.md 和使用說明
4. **依賴清單**：維護 `requirements.txt`
5. **測試充分**：打包前完整測試所有功能
