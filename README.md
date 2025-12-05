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

### 🔥 如果有些内文没有辨识出来？

**最简单有效的方法：启用图像预处理**

```bash
# 启用预处理（强烈推荐！）
python3 ocr_parser.py --image form.jpg --preprocess

# 🆕 启用高敏感度模式（识别更多文字）
python3 ocr_parser.py --image form.jpg --high-sensitivity

# 🌟 终极组合（预处理 + 高敏感度）
python3 ocr_parser.py --image form.jpg --preprocess --high-sensitivity

# 查看效果对比（测试4种模式）
python3 test_ocr.py form.jpg
```

在代码中使用：

```python
# 启用预处理可大幅提升识别率
parser = FormParser(enable_preprocessing=True)
result = parser.parse_form("form.jpg")

# 🆕 启用高敏感度（识别更多文字）
parser = FormParser(high_sensitivity=True)
result = parser.parse_form("form.jpg")

# 🌟 终极组合（推荐！）
parser = FormParser(
    enable_preprocessing=True,
    high_sensitivity=True
)
result = parser.parse_form("form.jpg")
```

**预处理可以解决以下问题：**
- ✅ 图像模糊
- ✅ 光照不均匀
- ✅ 对比度低
- ✅ 有噪点污渍
- ✅ 拍照倾斜
- ✅ 小字体识别不清

**🆕 高敏感度模式可以：**
- ✅ 识别更多文字（+30~50%）
- ✅ 识别小字体文字
- ✅ 识别低对比度文字
- ✅ 识别模糊文字

**详细改善方法请查看：**
📚 [OCR 辨识率改善完整指南](OCR_IMPROVEMENT_GUIDE.md)  
📚 [高敏感度模式使用指南](HIGH_SENSITIVITY_GUIDE.md)

---

### 提高识别精度

1. **🌟 使用图像预处理 + 高敏感度**（最推荐！）
   ```bash
   python3 ocr_parser.py --image form.jpg --preprocess --high-sensitivity
   ```

2. **使用图像预处理**（推荐）
   ```bash
   python3 ocr_parser.py --image form.jpg --preprocess
   ```

3. **🆕 使用高敏感度模式**（识别更多文字）
   ```bash
   python3 ocr_parser.py --image form.jpg --high-sensitivity
   ```

4. 使用清晰的图像（推荐 1000-3000px）
5. 确保光线充足均匀
6. 避免严重倾斜（会自动矫正小角度）
7. 保持对比度清晰

### 提高识别速度

```bash
# 使用 GPU（需要 CUDA）
python3 ocr_parser.py --image form.jpg --use-gpu
```

## 📦 项目结构

```
Paddle_Form_OCR/
├── form_parser.py              # 核心解析类
├── image_preprocessor.py       # 图像预处理模块（新）
├── ocr_parser.py               # 命令行工具
├── test_ocr.py                 # OCR效果测试脚本（新）
├── requirements.txt            # 依赖包列表
├── README.md                   # 说明文档
├── OCR_IMPROVEMENT_GUIDE.md    # 识别率改善指南（新）
└── examples/                   # 示例图像目录
```

## 🆘 常见问题

**Q: 有些内文没有辨识出来怎么办？**  
A: 启用图像预处理：`python3 ocr_parser.py --image form.jpg --preprocess`  
   详见 [OCR_IMPROVEMENT_GUIDE.md](OCR_IMPROVEMENT_GUIDE.md)

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

# 测试识别效果（对比预处理前后）
python3 test_ocr.py form.jpg

# 运行基础测试
python3 form_parser.py
```

**📚 详细文档：**
- [OCR 辨识率改善完整指南](OCR_IMPROVEMENT_GUIDE.md) - 解决识别不全的问题
- [图像预处理说明](image_preprocessor.py) - 了解预处理原理

## 🌟 技术栈

- **PaddleOCR** - 百度开源的 OCR 引擎
- **OpenCV** - 图像处理
- **NumPy** - 数值计算
- **Pillow** - 图像读取

---

**完全离线，永久免费，保护隐私！** 🎉
