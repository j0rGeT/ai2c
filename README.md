# AI内容创作系统 (AI2C)

一个基于Python的AI驱动内容创作系统，支持文章写作、小说创作、语音识别、视频生成和提示词优化等功能。

## 功能特性

### 1. 文章和小说生成
- 支持多种文章风格和长度
- 小说章节生成
- 故事大纲创建
- 支持DeepSeek（默认）、OpenAI和Anthropic模型

### 2. 语音识别和总结
- 基于Whisper的高精度语音识别
- 自动生成Markdown格式的转录文档
- 智能内容摘要和要点提取
- 支持长音频文件分段处理

### 3. 文本转视频
- 根据文本提示生成视频脚本
- 自动创建文字视频和幻灯片视频
- 支持多种视频风格和时长
- 可添加背景音乐和转场效果

### 4. AI图像生成
- 文本描述生成高质量图片
- 支持多种艺术风格（写实、动漫、油画等）
- 多个AI模型选择（Stable Diffusion系列）
- 智能提示词优化

### 5. 图片转视频
- 静态图片转动态视频
- 幻灯片视频制作
- 单图动画效果（缩放、平移、淡入淡出）
- 图片对比视频生成

### 6. 提示词优化
- 智能分析提示词质量
- 提供针对性优化建议
- 生成多个提示词变体
- 支持结构化提示词创建

## 安装和配置

### 1. 安装依赖

基础功能安装（文章写作、语音识别、提示词优化）：
```bash
pip install -r requirements.txt
```

可选：安装视频生成功能：
```bash
pip install -r requirements-video.txt
```

可选：安装图像生成功能：
```bash
pip install -r requirements-image.txt
```

完整安装（所有功能）：
```bash
pip install -r requirements-full.txt
```

### 2. 配置API密钥
复制 `.env.example` 为 `.env` 并填入你的API密钥：
```bash
cp .env.example .env
```

编辑 `.env` 文件（默认使用DeepSeek）：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

DEFAULT_LLM_PROVIDER=deepseek
```

### 3. 创建输出目录
```bash
mkdir -p outputs/{videos,audio,articles}
```

## 使用方法

### Web界面（推荐）

**快速启动：**
```bash
./run.sh
```

**手动启动：**
```bash
python start_web.py
```

**或直接运行：**
```bash
streamlit run web_app.py
```

Web界面功能：
- 🏠 **友好首页** - 功能概览和快速入口
- 📝 **智能写作** - 可视化文章生成界面
- 📚 **小说创作** - 章节和大纲生成工具
- 🎤 **语音处理** - 拖拽上传音频文件
- 🎬 **视频制作** - 文本转视频生成器
- ✨ **提示词优化** - 智能分析和优化工具

访问地址：`http://localhost:8501`

### 交互模式
```bash
python main.py --interactive
```

### 命令行模式

#### 生成文章
```bash
python main.py --article "人工智能的发展趋势"
```

#### 处理音频
```bash
python main.py --audio "path/to/audio.wav"
```

#### 生成视频
```bash
python main.py --video "介绍Python编程基础"
```

#### 优化提示词
```bash
python main.py --optimize-prompt "写一篇关于AI的文章"
```

## API 使用示例

### 文章生成
```python
from src.content_generation.content_generator import ContentGenerator

generator = ContentGenerator()
result = generator.generate_article(
    topic="机器学习入门",
    style="informative",
    length="medium"
)
filepath = generator.save_content(result)
```

### 语音处理
```python
from src.speech_recognition.speech_processor import SpeechProcessor

processor = SpeechProcessor()
result = processor.transcribe_and_summarize(
    audio_path="meeting.wav",
    language="zh",
    summary_type="会议纪要"
)
filepath = processor.save_results(result)
```

### 视频生成
```python
from src.video_generation.video_generator import VideoGenerator

generator = VideoGenerator()
result = generator.generate_video_from_text(
    text_prompt="Python基础教程",
    video_style="教育",
    duration=30
)
```

### 提示词优化
```python
from src.prompt_optimization.prompt_optimizer import PromptOptimizer

optimizer = PromptOptimizer()
result = optimizer.optimize_prompt(
    original_prompt="写一个故事",
    optimization_goal="全面优化",
    target_domain="创意"
)
```

## 项目结构
```
ai2c/
├── src/
│   ├── content_generation/     # 内容生成模块
│   ├── speech_recognition/     # 语音识别模块
│   ├── video_generation/       # 视频生成模块
│   └── prompt_optimization/    # 提示词优化模块
├── outputs/                    # 输出文件目录
├── requirements.txt            # 项目依赖
├── .env.example               # 环境变量模板
└── main.py                    # 主程序入口
```

## 注意事项

1. **API密钥**: 默认使用DeepSeek，需要配置相应API密钥才能使用内容生成功能
2. **Whisper模型**: 使用本地Whisper模型，首次运行时会自动下载到本地
3. **依赖安装**: 某些功能需要额外的系统依赖（如FFmpeg用于视频处理）
4. **文件格式**: 支持常见的音频格式（wav, mp3, m4a等）
5. **输出文件**: 所有生成的文件都保存在outputs目录中
6. **模型切换**: 可在环境变量中设置DEFAULT_LLM_PROVIDER来切换默认模型

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。