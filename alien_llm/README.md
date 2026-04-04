# Alien Signal Generator

**外星文明信号解读器**

一个交互式Web应用程序，用于模拟不同外星文明如何解读来自地球的信号。该应用使用微软的Phi-3语言模型生成基于选定星球特征的外星视角解释。

## 概述

Alien Signal Generator 是一个有趣的概念性项目，允许用户：

- 从12种不同的地球信号中选择3个（包括人口数据、人类图像、基因信息、动物、行星信息等）
- 选择一个外星星球作为接收信号的文明
- 调整AI参数（温度、最大token数）
- 查看所选外星文明如何解读这些地球信号

该项目结合了人工智能、天文学和科幻概念，为用户提供了独特的体验，展示了不同文明可能如何理解我们的世界。

## 项目结构

```
alien_llm/
├── models/phi3/           # Phi-3语言模型文件
├── scripts/
│   ├── server.py          # Flask后端服务器
│   ├── requirements.txt   # Python依赖
│   └── static/
│       └── index.html     # 前端界面
├── signals/
│   ├── nfc_info.json      # 地球信号数据
│   └── planet_info.json   # 外星星球数据
├── Raw_Data/
│   └── Raw.json           # 原始信号数据
├── .gitignore
└── README.md
```

## 技术栈

### 后端
- **Python**: Flask框架
- **PyTorch**: 深度学习框架
- **Transformers**: Hugging Face的模型库
- **Flask-CORS**: 跨域资源共享支持

### 前端
- **HTML/CSS/JavaScript**: 现代Web界面
- **Space主题设计**: 独特的太空风格UI

### AI模型
- **Microsoft Phi-3**: 3.8B参数的轻量级语言模型
- 支持Apple Silicon (MPS)加速

## 安装与运行

### 先决条件
- Python 3.8+
- 至少8GB可用磁盘空间（用于模型文件）
- macOS或Linux系统（推荐，Windows也可运行）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd alien_llm
   ```

2. **安装Python依赖**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

3. **下载Phi-3模型**
   访问 [Microsoft Phi-3 Mini 4K Instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) 并下载模型文件到 `models/phi3/` 目录：
   
   必需文件：
   - `config.json`
   - `tokenizer.json`
   - `tokenizer.model`
   - `tokenizer_config.json`
   - `special_tokens_map.json`
   - `model.safetensors.index.json`
   - `model-00001-of-00002.safetensors`
   - `model-00002-of-00002.safetensors`
   - `generation_config.json`
   - `modeling_phi3.py`
   - `configuration_phi3.py`
   - `added_tokens.json`

   或者使用Hugging Face Hub自动下载：
   ```bash
   pip install huggingface_hub
   huggingface-cli download microsoft/Phi-3-mini-4k-instruct --local-dir ./models/phi3
   ```

4. **启动服务器**
   ```bash
   python server.py
   ```

5. **访问应用**
   打开浏览器并前往 `http://localhost:5000`

## 数据集说明

### 地球信号 (signals/nfc_info.json)
包含12种不同类型的地球信号：

1. **Population(8340995923)**: 人口统计数据
2. **Human**: 人类形象
3. **Gene Pairs(3101804739)**: 基因信息
4. **Cat**: 猫的图像
5. **Dog**: 狗的图像
6. **Earth**: 地球图像
7. **Solar System**: 太阳系图示
8. **Mondrian**: 蒙德里安抽象艺术
9. **Apple**: 苹果图像
10. **DNA**: DNA分子结构
11. **Heart**: 心形符号
12. **Natural Number**: 自然数序列

### 外星星球 (signals/planet_info.json)
包含6个潜在宜居的系外行星：

1. **Proxima Centauri b**: 生存适应型文明，环境模式感知
2. **Kepler-452b**: 农业科学型文明，系统分析感知
3. **Kepler-186f**: 水生态型文明，生物解释感知
4. **TRAPPIST-1e**: 科学型文明，模式分析感知
5. **Gliese 667 Cc**: 矿物基础型文明，结构逻辑感知
6. **K2-18b**: 海洋型文明，流体模式识别感知

## 功能特性

- **交互式界面**: 现代化的太空主题UI设计
- **参数调整**: 可调节AI温度和最大输出长度
- **历史记录**: 保存和回顾之前的生成结果
- **数据导出/导入**: 支持JSON格式的数据备份
- **随机化选项**: 可随机选择星球
- **响应式设计**: 适配不同屏幕尺寸

## 使用指南

1. 在左侧面板选择3个地球信号
2. 选择一个外星星球或使用"随机星球"功能
3. 调整AI参数（可选）
4. 点击"生成结果"按钮
5. 查看外星文明对地球信号的解读
6. 结果会自动保存在历史记录中

## 配置选项

- **Temperature**: 控制输出的随机性（0.1-1.5）
  - 较低值：更确定性和保守的输出
  - 较高值：更多样化和创造性的输出
- **Max Tokens**: 控制生成文本的最大长度（20-200）

## 故障排除

### 模型加载问题
如果遇到内存不足错误，请确保：
- 至少有8GB可用RAM
- 模型文件完整且正确放置在 `models/phi3/` 目录

### 服务器无法启动
检查端口5000是否被占用：
```bash
lsof -i :5000
```

### CORS错误
确保后端服务器正常运行且前端通过正确的URL访问。

## 性能提示

- 在Apple Silicon Mac上，应用会自动使用MPS加速
- 对于CPU运行，可能需要较长时间来处理请求
- 初始模型加载可能需要几秒钟

## 开发

如有兴趣扩展此项目，可以考虑：
- 添加更多地球信号类型
- 添加更多外星星球和文明类型
- 实现更复杂的AI交互逻辑
- 增加多语言支持

## 许可证

本项目使用Phi-3模型，遵循MIT许可证。具体请参阅模型的许可证文件。

## 贡献

欢迎提交Issue和Pull Request来改进此项目！

## 致谢

- Microsoft Phi-3模型团队
- Hugging Face Transformers库
- Flask Web框架