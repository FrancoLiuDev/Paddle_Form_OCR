FROM python:3.10-slim

LABEL maintainer="Offline OCR Project"
LABEL description="离线 OCR 表单解析服务（基于 PaddleOCR）"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY form_parser.py .
COPY ocr_parser.py .
COPY example.py .

# 创建必要的目录
RUN mkdir -p /app/examples /app/output /app/results

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 预下载 PaddleOCR 模型
RUN python3 -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)"

# 默认命令
CMD ["python3", "example.py"]
