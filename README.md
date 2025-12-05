# 离线 OCR 表单解析项目

## ✨ 完全离线，无需 API

使用 **PaddleOCR** 开源引擎进行文字识别

### 特点

- ✅ **完全离线** - 无需网络连接
- ✅ **无需 API Key** - 不需要注册任何服务
- ✅ **永久免费** - 开源免费
- ✅ **隐私安全** - 数据不离开本地
- ✅ **支持中英文** - 80+ 种语言
- ✅ **高精度识别** - 基于深度学习

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt --user
```

首次运行会自动下载模型文件（约 20-30MB）

### 2. 开始使用

```bash
# 识别单个表单
python3 ocr_parser.py --image form.jpg

# 查看详细结果
python3 ocr_parser.py --image form.jpg --verbose --pretty-print

# 保存结果
python3 ocr_parser.py --image form.jpg --output result.json

# 批量处理
python3 ocr_parser.py --image *.jpg --output-dir results/

# 生成可视化图像（标注识别框）
python3 ocr_parser.py --image form.jpg --visualize output_visual.jpg
```

## 📝 使用示例

### 命令行方式

```bash
# 中英文混合识别
python3 ocr_parser.py --image form.jpg --lang ch_en

# 使用 GPU 加速（需要 NVIDIA GPU + CUDA）
python3 ocr_parser.py --image form.jpg --use-gpu

# 批量处理并生成可视化
python3 ocr_parser.py --image examples/*.jpg --output-dir results/ --visualize
```

### Python 代码方式

```python
from form_parser import FormParser

# 初始化解析器
parser = FormParser(lang='ch', use_gpu=False)

# 解析表单
result = parser.parse_form("form.jpg")

# 查看结果
print(result)

# 保存结果
parser.save_result(result, "output.json")

# 生成可视化图像
parser.visualize_result("form.jpg", result, "visual.jpg")

# 批量处理
results = parser.parse_multiple_forms(["form1.jpg", "form2.jpg"])
```

## 📊 输出格式

```json
{
  "success": true,
  "image_path": "form.jpg",
  "text_blocks": [
    {
      "text": "姓名",
      "confidence": 0.98,
      "position": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ],
  "full_text": "完整的识别文字...",
  "fields": {
    "姓名": "张三",
    "身份证": "123456789..."
  },
  "total_blocks": 10,
  "ocr_engine": "PaddleOCR (Offline)"
}
```

## 🎯 支持的功能

- ✅ 中文识别
- ✅ 英文识别  
- ✅ 中英混合识别
- ✅ 数字识别
- ✅ 表格识别
- ✅ 倾斜矫正
- ✅ 批量处理
- ✅ 结果可视化
- ✅ GPU 加速

## 💡 优化建议

### 提高识别精度

1. 使用清晰的图像（推荐 1000-3000px）
2. 确保光线充足
3. 避免严重倾斜（会自动矫正小角度）
4. 对比度要清晰

### 提高识别速度

```bash
# 使用 GPU（需要 CUDA）
python3 ocr_parser.py --image form.jpg --use-gpu
```

## 📦 项目结构

```
deepseek_form/
├── form_parser.py      # 核心解析类
├── ocr_parser.py       # 命令行工具
├── requirements.txt    # 依赖包列表
├── README.md          # 说明文档
└── examples/          # 示例图像目录
```

## 🆘 常见问题

**Q: 需要网络连接吗？**  
A: 首次运行需要下载模型（约 20-30MB），之后完全离线

**Q: 识别速度慢怎么办？**  
A: 使用 `--use-gpu` 参数开启 GPU 加速

**Q: 支持哪些语言？**  
A: 支持 80+ 种语言，中文和英文效果最好

**Q: 和 API 方案相比如何？**  
A: 离线方案完全免费且保护隐私，API 方案精度可能更高

**Q: 可以识别表格吗？**  
A: 可以，PaddleOCR 支持表格结构识别

## 📖 更多帮助

```bash
# 查看命令行帮助
python3 ocr_parser.py --help

# 运行测试
python3 form_parser.py
```

## 🌟 技术栈

- **PaddleOCR** - 百度开源的 OCR 引擎
- **OpenCV** - 图像处理
- **NumPy** - 数值计算
- **Pillow** - 图像读取

---

**完全离线，永久免费，保护隐私！** 🎉
