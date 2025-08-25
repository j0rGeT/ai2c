#!/usr/bin/env python3
"""
AI内容创作系统 - Streamlit Web界面
提供可视化的交互界面用于内容生成、语音处理、视频制作和提示词优化
"""

import streamlit as st
import os
import io
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from PIL import Image

# 页面配置
st.set_page_config(
    page_title="AI内容创作系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入系统模块
from src.content_generation.content_generator import ContentGenerator
from src.speech_recognition.speech_processor import SpeechProcessor
from src.prompt_optimization.prompt_optimizer import PromptOptimizer
from src.web_utils import custom_css, display_system_info, show_help_section

# 可选视频生成模块
try:
    from src.video_generation.video_generator import VideoGenerator
    VIDEO_GENERATION_AVAILABLE = True
except ImportError:
    VIDEO_GENERATION_AVAILABLE = False

# 可选图像生成模块
try:
    from src.image_generation.text_to_image import TextToImageGenerator
    from src.image_generation.image_to_video import ImageToVideoGenerator
    from src.image_generation.image_editor import ImageEditor
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False

# 初始化session state
if 'content_generator' not in st.session_state:
    st.session_state.content_generator = ContentGenerator()
if 'speech_processor' not in st.session_state:
    st.session_state.speech_processor = SpeechProcessor()
if 'prompt_optimizer' not in st.session_state:
    st.session_state.prompt_optimizer = PromptOptimizer()
if VIDEO_GENERATION_AVAILABLE and 'video_generator' not in st.session_state:
    st.session_state.video_generator = VideoGenerator()
if IMAGE_GENERATION_AVAILABLE and 'text_to_image' not in st.session_state:
    st.session_state.text_to_image = TextToImageGenerator()
if IMAGE_GENERATION_AVAILABLE and 'image_to_video' not in st.session_state:
    st.session_state.image_to_video = ImageToVideoGenerator()
if IMAGE_GENERATION_AVAILABLE and 'image_editor' not in st.session_state:
    st.session_state.image_editor = ImageEditor()

# 应用自定义CSS样式
custom_css()

def main():
    # 主标题
    st.markdown('<h1 class="main-header">🤖 AI内容创作系统</h1>', unsafe_allow_html=True)
    
    # 侧边栏导航
    st.sidebar.title("功能导航")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "选择功能模块",
        [
            "🏠 首页",
            "📝 文章写作",
            "📚 小说创作",
            "🎤 语音识别",
            "🎬 视频生成" if VIDEO_GENERATION_AVAILABLE else "🎬 视频生成 (不可用)",
            "🎨 文本生成图片" if IMAGE_GENERATION_AVAILABLE else "🎨 文本生成图片 (不可用)",
            "🖼️ 图像编辑" if IMAGE_GENERATION_AVAILABLE else "🖼️ 图像编辑 (不可用)",
            "🎞️ 图片转视频" if IMAGE_GENERATION_AVAILABLE and VIDEO_GENERATION_AVAILABLE else "🎞️ 图片转视频 (不可用)",
            "✨ 提示词优化"
        ]
    )
    
    # 显示系统状态
    display_system_info()
    
    # 显示帮助信息
    st.sidebar.markdown("---")
    show_help_section()
    
    # 路由到不同页面
    if page == "🏠 首页":
        show_home_page()
    elif page == "📝 文章写作":
        show_article_generation()
    elif page == "📚 小说创作":
        show_novel_generation()
    elif page == "🎤 语音识别":
        show_speech_recognition()
    elif page.startswith("🎬 视频生成"):
        show_video_generation()
    elif page.startswith("🎨 文本生成图片"):
        show_text_to_image()
    elif page.startswith("🖼️ 图像编辑"):
        show_image_editing()
    elif page.startswith("🎞️ 图片转视频"):
        show_image_to_video()
    elif page == "✨ 提示词优化":
        show_prompt_optimization()


def show_home_page():
    """显示首页"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🚀 欢迎使用AI内容创作系统
        
        这是一个功能强大的AI驱动内容创作平台，支持多种创作需求：
        
        ### 🌟 主要功能
        
        - **📝 智能写作**: 生成高质量文章和内容
        - **📚 小说创作**: 章节生成和故事大纲创建
        - **🎤 语音处理**: Whisper语音识别和智能摘要
        - **🎬 视频制作**: 文本转视频，自动脚本生成
        - **🎨 图像生成**: AI文本生成图片，多种风格支持
        - **🖼️ 图像编辑**: Qwen-Image-Edit视角转换，风格变换
        - **🎞️ 图片转视频**: 静态图片转动态视频，幻灯片制作
        - **✨ 提示词优化**: 智能分析和优化提示词质量
        
        ### 🛠 技术特性
        
        - 支持多个LLM提供商（DeepSeek、OpenAI、Anthropic）
        - 本地Whisper模型，保护隐私
        - 模块化设计，可选功能安装
        - 友好的Web界面和命令行界面
        """)
    
    with col2:
        st.markdown("""
        ### 📊 使用统计
        """)
        
        # 显示一些使用统计（示例）
        st.metric("支持的文件格式", "15+")
        st.metric("功能模块", "7个")
        st.metric("支持语言", "中英文")
        
        st.markdown("### 🔗 快速链接")
        if st.button("📝 开始写作", use_container_width=True):
            st.session_state.page = "📝 文章写作"
            st.rerun()
        if st.button("🎤 处理音频", use_container_width=True):
            st.session_state.page = "🎤 语音识别"
            st.rerun()
        if st.button("🎨 生成图片", use_container_width=True):
            st.session_state.page = "🎨 文本生成图片"
            st.rerun()
        if st.button("🖼️ 编辑图片", use_container_width=True):
            st.session_state.page = "🖼️ 图像编辑"
            st.rerun()
        if st.button("🎞️ 制作视频", use_container_width=True):
            st.session_state.page = "🎞️ 图片转视频"
            st.rerun()

def show_article_generation():
    """文章生成页面"""
    st.header("📝 智能文章写作")
    
    with st.form("article_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "文章主题 *",
                placeholder="例如: 人工智能的发展趋势",
                help="描述你想要写作的主题"
            )
            
            style = st.selectbox(
                "写作风格",
                ["informative", "narrative", "persuasive", "technical", "casual"],
                format_func=lambda x: {
                    "informative": "信息性 - 客观介绍",
                    "narrative": "叙述性 - 故事化表达", 
                    "persuasive": "说服性 - 观点论证",
                    "technical": "技术性 - 专业详细",
                    "casual": "轻松性 - 对话风格"
                }[x]
            )
        
        with col2:
            length = st.selectbox(
                "文章长度",
                ["short", "medium", "long"],
                index=1,
                format_func=lambda x: {
                    "short": "短篇 (500-800字)",
                    "medium": "中篇 (1000-1500字)",
                    "long": "长篇 (2000-3000字)"
                }[x]
            )
            
            provider = st.selectbox(
                "AI模型",
                ["默认", "deepseek", "openai", "anthropic"],
                help="选择使用的AI模型"
            )
        
        submitted = st.form_submit_button("🚀 生成文章", use_container_width=True)
    
    if submitted and topic:
        with st.spinner("正在生成文章，请稍候..."):
            try:
                provider_value = None if provider == "默认" else provider
                result = st.session_state.content_generator.generate_article(
                    topic, style, length, provider_value
                )
                
                if result:
                    st.success("✅ 文章生成成功！")
                    
                    # 显示文章内容
                    st.markdown("### 📄 生成的文章")
                    st.markdown(f"**标题**: {result['title']}")
                    st.markdown("---")
                    st.markdown(result['content'])
                    
                    # 显示元数据
                    with st.expander("📊 文章信息"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("字数", result['metadata']['word_count'])
                        with col2:
                            st.metric("风格", result['metadata']['style'])
                        with col3:
                            st.metric("长度", result['metadata']['length'])
                    
                    # 保存文件
                    if st.button("💾 保存到文件"):
                        filepath = st.session_state.content_generator.save_content(result)
                        st.success(f"文件已保存到: {filepath}")
                
            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
    
    elif submitted:
        st.warning("⚠️ 请输入文章主题")

def show_novel_generation():
    """小说生成页面"""
    st.header("📚 智能小说创作")
    
    tab1, tab2 = st.tabs(["📖 章节生成", "📋 故事大纲"])
    
    with tab1:
        st.subheader("生成小说章节")
        
        with st.form("chapter_form"):
            plot = st.text_area(
                "章节剧情 *",
                height=100,
                placeholder="描述这一章节的主要情节发展...",
                help="详细描述章节的情节内容"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                characters = st.text_area(
                    "主要人物",
                    height=80,
                    placeholder="角色姓名、性格特点等...",
                    help="可选：描述本章涉及的主要人物"
                )
                chapter_number = st.number_input(
                    "章节编号", 
                    min_value=1, 
                    value=1,
                    help="当前章节的编号"
                )
            
            with col2:
                setting = st.text_area(
                    "背景设定",
                    height=80,
                    placeholder="时间、地点、环境描述...",
                    help="可选：章节的背景设定"
                )
                provider = st.selectbox(
                    "AI模型",
                    ["默认", "deepseek", "openai", "anthropic"]
                )
            
            submitted = st.form_submit_button("📝 生成章节", use_container_width=True)
        
        if submitted and plot:
            with st.spinner(f"正在创作第{chapter_number}章..."):
                try:
                    provider_value = None if provider == "默认" else provider
                    result = st.session_state.content_generator.generate_novel_chapter(
                        plot, characters, setting, chapter_number, provider_value
                    )
                    
                    if result:
                        st.success("✅ 章节生成成功！")
                        
                        st.markdown(f"### {result['title']}")
                        st.markdown("---")
                        st.markdown(result['content'])
                        
                        with st.expander("📊 章节信息"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("字数", result['metadata']['word_count'])
                                st.text(f"章节: {result['metadata']['chapter_number']}")
                            with col2:
                                st.text(f"生成时间: {result['metadata']['generated_at'][:19]}")
                        
                        if st.button("💾 保存章节", key="save_chapter"):
                            filepath = st.session_state.content_generator.save_content(result)
                            st.success(f"章节已保存到: {filepath}")
                
                except Exception as e:
                    st.error(f"❌ 生成失败: {str(e)}")
        elif submitted:
            st.warning("⚠️ 请输入章节剧情")
    
    with tab2:
        st.subheader("生成故事大纲")
        
        with st.form("outline_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                theme = st.text_input(
                    "小说主题 *",
                    placeholder="例如: 科幻冒险、都市爱情、历史传奇",
                    help="描述小说的主要主题"
                )
                genre = st.selectbox(
                    "小说类型",
                    ["现代", "古代", "科幻", "奇幻", "悬疑", "爱情", "历史"],
                    help="选择小说的类型背景"
                )
            
            with col2:
                length = st.selectbox(
                    "小说长度",
                    ["短篇", "中篇", "长篇"],
                    index=1,
                    help="确定小说的预期长度"
                )
                provider = st.selectbox(
                    "AI模型",
                    ["默认", "deepseek", "openai", "anthropic"],
                    key="outline_provider"
                )
            
            submitted = st.form_submit_button("📋 生成大纲", use_container_width=True)
        
        if submitted and theme:
            with st.spinner("正在创建故事大纲..."):
                try:
                    provider_value = None if provider == "默认" else provider
                    result = st.session_state.content_generator.generate_story_outline(
                        theme, genre, length, provider_value
                    )
                    
                    if result:
                        st.success("✅ 大纲生成成功！")
                        
                        st.markdown(f"### {result['title']}")
                        st.markdown("---")
                        st.markdown(result['content'])
                        
                        if st.button("💾 保存大纲", key="save_outline"):
                            filepath = st.session_state.content_generator.save_content(result)
                            st.success(f"大纲已保存到: {filepath}")
                
                except Exception as e:
                    st.error(f"❌ 生成失败: {str(e)}")
        elif submitted:
            st.warning("⚠️ 请输入小说主题")

def show_speech_recognition():
    """语音识别页面"""
    st.header("🎤 智能语音识别")
    
    st.markdown("""
    上传音频文件，系统将使用Whisper模型进行语音识别，并生成智能摘要。
    支持的格式：WAV, MP3, M4A, MP4 等
    """)
    
    uploaded_file = st.file_uploader(
        "选择音频文件",
        type=['wav', 'mp3', 'm4a', 'mp4', 'avi', 'mov'],
        help="支持常见的音频和视频格式"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "识别语言",
            ["zh", "en", "auto"],
            format_func=lambda x: {
                "zh": "中文",
                "en": "英文", 
                "auto": "自动检测"
            }[x],
            help="选择音频的主要语言"
        )
    
    with col2:
        summary_type = st.selectbox(
            "摘要类型",
            ["详细", "简要", "要点", "会议纪要"],
            help="选择生成摘要的详细程度"
        )
    
    if uploaded_file is not None:
        # 显示文件信息
        st.info(f"📁 文件: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)")
        
        if st.button("🚀 开始处理", use_container_width=True):
            # 保存上传的文件
            temp_path = f"./temp/{uploaded_file.name}"
            os.makedirs("./temp", exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            
            with st.spinner("正在进行语音识别和分析..."):
                try:
                    result = st.session_state.speech_processor.transcribe_and_summarize(
                        temp_path, language, summary_type
                    )
                    
                    if result:
                        st.success("✅ 处理完成！")
                        
                        # 显示结果标签页
                        tab1, tab2, tab3 = st.tabs(["📄 摘要", "📝 完整转录", "📊 详细信息"])
                        
                        with tab1:
                            st.markdown("### 🔍 智能摘要")
                            st.markdown(result['summary']['content'])
                        
                        with tab2:
                            st.markdown("### 📝 完整转录文本")
                            st.text_area(
                                "转录内容",
                                result['transcription']['full_text'],
                                height=300,
                                key="full_transcription"
                            )
                            
                            with st.expander("⏱️ 分段转录（带时间戳）"):
                                for segment in result['transcription'].get('segments', []):
                                    st.markdown(f"**{segment['start_time']} - {segment['end_time']}**")
                                    st.write(segment['text'])
                                    st.markdown("---")
                        
                        with tab3:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("音频时长", f"{result['metadata']['duration']:.1f}秒")
                            with col2:
                                st.metric("识别语言", result['transcription']['language'])
                            with col3:
                                st.metric("摘要字数", result['summary']['word_count'])
                        
                        # 下载选项
                        st.markdown("### 📥 下载选项")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                "下载完整报告 (Markdown)",
                                result['markdown'],
                                file_name=f"{uploaded_file.name}_transcript.md",
                                mime="text/markdown"
                            )
                        
                        with col2:
                            if st.button("💾 保存到服务器"):
                                filepath = st.session_state.speech_processor.save_results(result)
                                st.success(f"文件已保存到: {filepath}")
                
                except Exception as e:
                    st.error(f"❌ 处理失败: {str(e)}")
                
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

def show_video_generation():
    """视频生成页面"""
    st.header("🎬 智能视频生成")
    
    if not VIDEO_GENERATION_AVAILABLE:
        st.error("""
        ❌ 视频生成功能不可用
        
        请安装视频生成依赖：
        ```bash
        pip install -r requirements-video.txt
        ```
        """)
        return
    
    st.markdown("""
    根据文本描述自动生成视频脚本和视频内容。
    支持多种视频风格和时长设定。
    """)
    
    with st.form("video_form"):
        text_prompt = st.text_area(
            "视频内容描述 *",
            height=120,
            placeholder="例如: 介绍Python编程基础知识，包括变量、函数和循环...",
            help="详细描述想要制作的视频内容"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            video_style = st.selectbox(
                "视频风格",
                ["教育", "营销", "故事", "解说", "社交"],
                help="选择视频的整体风格"
            )
        
        with col2:
            duration = st.slider(
                "视频时长 (秒)",
                min_value=10,
                max_value=120,
                value=30,
                step=5,
                help="设定视频的总时长"
            )
        
        with col3:
            output_type = st.selectbox(
                "输出类型",
                ["text_video", "slideshow"],
                format_func=lambda x: {
                    "text_video": "文字视频",
                    "slideshow": "幻灯片视频"
                }[x],
                help="选择视频的输出格式"
            )
        
        submitted = st.form_submit_button("🎬 生成视频", use_container_width=True)
    
    if submitted and text_prompt:
        with st.spinner("正在生成视频脚本和制作视频..."):
            try:
                result = st.session_state.video_generator.generate_video_from_text(
                    text_prompt, video_style, duration, output_type
                )
                
                if result:
                    st.success("✅ 视频生成成功！")
                    
                    # 显示视频脚本
                    with st.expander("📋 查看生成的视频脚本"):
                        script = result['script']
                        st.json(script)
                    
                    # 显示视频信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("时长", f"{duration}秒")
                    with col2:
                        file_size = result['metadata']['file_size'] / (1024 * 1024)
                        st.metric("文件大小", f"{file_size:.1f}MB")
                    with col3:
                        st.metric("风格", video_style)
                    
                    # 视频预览和下载
                    if os.path.exists(result['video_path']):
                        st.markdown("### 🎥 视频预览")
                        st.video(result['video_path'])
                        
                        # 下载按钮
                        with open(result['video_path'], "rb") as video_file:
                            st.download_button(
                                "📥 下载视频",
                                video_file.read(),
                                file_name=os.path.basename(result['video_path']),
                                mime="video/mp4"
                            )
                    else:
                        st.error("视频文件未找到")
            
            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
                st.info("💡 提示：视频生成功能需要安装额外依赖")
    
    elif submitted:
        st.warning("⚠️ 请输入视频内容描述")

def show_prompt_optimization():
    """提示词优化页面"""
    st.header("✨ 智能提示词优化")
    
    st.markdown("""
    输入您的提示词，系统将分析其质量并提供优化建议，
    帮助您获得更好的AI响应效果。
    """)
    
    tab1, tab2, tab3 = st.tabs(["🔍 提示词分析", "✨ 智能优化", "🎯 结构化创建"])
    
    with tab1:
        st.subheader("分析现有提示词")
        
        original_prompt = st.text_area(
            "输入需要分析的提示词",
            height=150,
            placeholder="输入您想要分析的提示词...",
            help="粘贴您现有的提示词进行质量分析"
        )
        
        if st.button("🔍 开始分析", use_container_width=True):
            if original_prompt:
                with st.spinner("正在分析提示词质量..."):
                    try:
                        result = st.session_state.prompt_optimizer.analyze_prompt(original_prompt)
                        
                        if result and 'analysis' in result:
                            st.success("✅ 分析完成！")
                            
                            # 显示分析结果
                            st.markdown("### 📊 质量分析报告")
                            st.text_area(
                                "分析结果",
                                result['analysis'],
                                height=200,
                                key="analysis_result"
                            )
                            
                            # 显示评分（如果可用）
                            if 'scores' in result:
                                st.markdown("### 📈 各项评分")
                                scores = result['scores']
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if 'clarity_score' in scores:
                                        st.metric("清晰度", f"{scores['clarity_score']}/10")
                                    if 'specificity_score' in scores:
                                        st.metric("具体性", f"{scores['specificity_score']}/10")
                                
                                with col2:
                                    if 'structure_score' in scores:
                                        st.metric("结构性", f"{scores['structure_score']}/10")
                                    if 'completeness_score' in scores:
                                        st.metric("完整性", f"{scores['completeness_score']}/10")
                        else:
                            st.error("分析过程中出现问题")
                    
                    except Exception as e:
                        st.error(f"❌ 分析失败: {str(e)}")
            else:
                st.warning("⚠️ 请输入要分析的提示词")
    
    with tab2:
        st.subheader("优化提示词")
        
        with st.form("optimization_form"):
            prompt_to_optimize = st.text_area(
                "需要优化的提示词 *",
                height=120,
                placeholder="输入您想要优化的提示词...",
                help="系统将分析并提供优化建议"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                optimization_goal = st.selectbox(
                    "优化目标",
                    ["全面优化", "提高清晰度", "增强具体性", "改进结构", "提升可操作性"],
                    help="选择主要的优化方向"
                )
            
            with col2:
                target_domain = st.selectbox(
                    "应用领域",
                    ["通用", "写作", "分析", "创意", "技术", "教育", "营销"],
                    help="选择提示词的应用场景"
                )
            
            submitted = st.form_submit_button("✨ 开始优化", use_container_width=True)
        
        if submitted and prompt_to_optimize:
            with st.spinner("正在优化提示词..."):
                try:
                    result = st.session_state.prompt_optimizer.optimize_prompt(
                        prompt_to_optimize, optimization_goal, target_domain
                    )
                    
                    if result and 'result' in result:
                        st.success("✅ 优化完成！")
                        
                        st.markdown("### 🎯 优化结果")
                        st.text_area(
                            "优化后的提示词和建议",
                            result['result'],
                            height=300,
                            key="optimization_result"
                        )
                        
                        # 对比显示
                        with st.expander("📋 原始vs优化对比"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**原始提示词:**")
                                st.text_area("", prompt_to_optimize, height=150, key="original_compare")
                            with col2:
                                st.markdown("**优化建议:**")
                                st.text_area("", result['result'][:500] + "...", height=150, key="optimized_compare")
                
                except Exception as e:
                    st.error(f"❌ 优化失败: {str(e)}")
        
        elif submitted:
            st.warning("⚠️ 请输入需要优化的提示词")
    
    with tab3:
        st.subheader("结构化提示词创建")
        
        with st.form("structured_form"):
            task_description = st.text_area(
                "任务描述 *",
                height=100,
                placeholder="描述您希望AI完成的具体任务...",
                help="清晰描述您的需求"
            )
            
            role_context = st.text_area(
                "角色设定",
                height=80,
                placeholder="例如: 你是一个专业的内容创作者...",
                help="可选：为AI设定特定的角色身份"
            )
            
            output_format = st.text_area(
                "输出格式要求",
                height=80,
                placeholder="例如: 请以Markdown格式输出，包含标题和段落...",
                help="指定期望的输出格式"
            )
            
            constraints = st.text_area(
                "约束条件",
                height=80,
                placeholder="每行一个约束条件...",
                help="可选：列出需要遵守的限制条件"
            )
            
            examples = st.text_area(
                "示例",
                height=80,
                placeholder="提供一些示例...",
                help="可选：提供参考示例"
            )
            
            submitted = st.form_submit_button("🎯 生成结构化提示词", use_container_width=True)
        
        if submitted and task_description:
            try:
                # 处理约束条件和示例
                constraints_list = [c.strip() for c in constraints.split('\n') if c.strip()] if constraints else []
                examples_list = [e.strip() for e in examples.split('\n\n') if e.strip()] if examples else []
                
                result = st.session_state.prompt_optimizer.create_structured_prompt(
                    task_description, output_format, role_context, constraints_list, examples_list
                )
                
                if result:
                    st.success("✅ 结构化提示词生成成功！")
                    
                    st.markdown("### 📝 生成的结构化提示词")
                    st.text_area(
                        "结构化提示词",
                        result['structured_prompt'],
                        height=400,
                        key="structured_result"
                    )
                    
                    # 复制按钮功能
                    st.markdown("### 📋 使用说明")
                    st.info("您可以复制上面的提示词直接使用，或根据需要进一步调整。")
            
            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
        
        elif submitted:
            st.warning("⚠️ 请输入任务描述")

def show_text_to_image():
    """文本生成图片页面"""
    st.header("🎨 智能文本生成图片")
    
    if not IMAGE_GENERATION_AVAILABLE:
        st.error("""
        ❌ 图像生成功能不可用
        
        请安装图像生成依赖：
        ```bash
        pip install -r requirements-image.txt
        ```
        
        注意：首次使用需要下载大型AI模型，请确保有足够的存储空间和网络带宽。
        """)
        return
    
    st.markdown("""
    使用AI根据文本描述生成高质量图片。
    支持多种艺术风格和尺寸设定。
    """)
    
    with st.form("image_generation_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt = st.text_area(
                "图片描述 *",
                height=120,
                placeholder="例如: 一只可爱的橘猫坐在窗台上，阳光透过窗户照在它身上，背景是蓝天白云",
                help="详细描述您想要生成的图片内容"
            )
            
            negative_prompt = st.text_area(
                "负面提示词（可选）",
                height=60,
                placeholder="不希望出现的内容，例如: 模糊, 低质量, 变形",
                help="描述不希望在图片中出现的元素"
            )
        
        with col2:
            style = st.selectbox(
                "艺术风格",
                ["写实", "动漫", "油画", "水彩", "素描", "卡通", "科幻", "梦幻"],
                help="选择图片的艺术风格"
            )
            
            model_name = st.selectbox(
                "AI模型",
                ["sd15", "sdxl", "sd21"],
                format_func=lambda x: {
                    "sd15": "Stable Diffusion 1.5 (快速)",
                    "sdxl": "Stable Diffusion XL (高质量)",
                    "sd21": "Stable Diffusion 2.1 (平衡)"
                }[x],
                help="选择使用的AI模型"
            )
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                width = st.selectbox("宽度", [512, 768, 1024], index=0)
                num_images = st.slider("生成数量", 1, 4, 1)
            
            with col2_2:
                height = st.selectbox("高度", [512, 768, 1024], index=0)
                steps = st.slider("生成步数", 10, 50, 20, help="更多步数=更高质量,但更慢")
        
        advanced = st.expander("🔧 高级设置")
        with advanced:
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                guidance_scale = st.slider(
                    "引导强度", 
                    1.0, 20.0, 7.5, 0.5,
                    help="控制AI对提示词的遵循程度"
                )
                optimize_prompt = st.checkbox("优化提示词", value=True, help="使用AI优化您的提示词")
            with col3_2:
                seed = st.number_input(
                    "随机种子 (可选)", 
                    min_value=0, max_value=2**32-1, value=0,
                    help="设置为0使用随机种子，固定数值可重现结果"
                )
        
        submitted = st.form_submit_button("🎨 生成图片", use_container_width=True)
    
    if submitted and prompt:
        with st.spinner("正在生成图片，请稍候..."):
            try:
                result = st.session_state.text_to_image.generate_image(
                    prompt=prompt,
                    style=style,
                    width=width,
                    height=height,
                    num_images=num_images,
                    steps=steps,
                    guidance_scale=guidance_scale,
                    negative_prompt=negative_prompt if negative_prompt else None,
                    seed=seed if seed > 0 else None,
                    optimize_prompt=optimize_prompt,
                    model_name=model_name
                )
                
                if result:
                    st.success("✅ 图片生成成功！")
                    
                    # 显示生成的图片
                    st.markdown("### 🖼️ 生成结果")
                    
                    if len(result['images']) == 1:
                        st.image(result['images'][0], caption=f"生成的图片", use_column_width=True)
                    else:
                        # 多图显示
                        cols = st.columns(min(len(result['images']), 2))
                        for i, image in enumerate(result['images']):
                            with cols[i % len(cols)]:
                                st.image(image, caption=f"图片 {i+1}", use_column_width=True)
                    
                    # 显示生成信息
                    with st.expander("📊 生成信息"):
                        metadata = result['metadata']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("尺寸", f"{metadata['width']}×{metadata['height']}")
                            st.metric("生成步数", metadata['steps'])
                        
                        with col2:
                            st.metric("风格", metadata['style'])
                            st.metric("引导强度", metadata['guidance_scale'])
                        
                        with col3:
                            st.metric("随机种子", metadata['seed'])
                            st.metric("AI模型", metadata['model_name'])
                        
                        st.text_area("优化后的提示词", metadata['prompt'], height=100, key="optimized_prompt_display")
                    
                    # 下载选项
                    st.markdown("### 📥 下载图片")
                    for i, (image, path) in enumerate(zip(result['images'], result['saved_paths'])):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(f"图片 {i+1}: {os.path.basename(path)}")
                        with col2:
                            # 将PIL图像转换为字节
                            img_bytes = io.BytesIO()
                            image.save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "下载",
                                data=img_bytes,
                                file_name=os.path.basename(path),
                                mime="image/png",
                                key=f"download_img_{i}"
                            )
            
            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
                if "CUDA" in str(e) or "memory" in str(e).lower():
                    st.info("💡 提示：如果遇到显存不足错误，可以尝试减少生成步数或降低图片尺寸")
    
    elif submitted:
        st.warning("⚠️ 请输入图片描述")

def show_image_to_video():
    """图片转视频页面"""
    st.header("🎞️ 智能图片转视频")
    
    if not (IMAGE_GENERATION_AVAILABLE and VIDEO_GENERATION_AVAILABLE):
        st.error("""
        ❌ 图片转视频功能不可用
        
        需要安装以下依赖：
        ```bash
        pip install -r requirements-image.txt
        pip install -r requirements-video.txt
        ```
        """)
        return
    
    st.markdown("""
    将静态图片转换为动态视频，支持多种效果和转场。
    可以创建幻灯片、动画效果或对比视频。
    """)
    
    tab1, tab2, tab3 = st.tabs(["📸 幻灯片视频", "🎬 单图动画", "⚖️ 对比视频"])
    
    with tab1:
        st.subheader("创建幻灯片视频")
        
        uploaded_files = st.file_uploader(
            "上传图片文件",
            type=['png', 'jpg', 'jpeg', 'webp'],
            accept_multiple_files=True,
            help="支持多张图片，将按上传顺序排列"
        )
        
        if uploaded_files:
            st.success(f"已上传 {len(uploaded_files)} 张图片")
            
            # 显示预览
            with st.expander("🔍 图片预览"):
                cols = st.columns(min(len(uploaded_files), 4))
                for i, file in enumerate(uploaded_files):
                    with cols[i % len(cols)]:
                        st.image(file, caption=file.name, use_column_width=True)
            
            # 设置参数
            col1, col2 = st.columns(2)
            
            with col1:
                duration_per_image = st.slider(
                    "每张图片显示时长 (秒)", 
                    1.0, 10.0, 3.0, 0.5,
                    help="每张图片在视频中的显示时间"
                )
                
                transition_duration = st.slider(
                    "转场时长 (秒)", 
                    0.0, 2.0, 0.5, 0.1,
                    help="图片之间的淡入淡出时间"
                )
            
            with col2:
                output_width = st.selectbox("视频宽度", [1280, 1920, 3840], index=1)
                output_height = st.selectbox("视频高度", [720, 1080, 2160], index=1)
                fps = st.selectbox("帧率", [24, 30, 60], index=1)
            
            # 背景音乐
            background_music = st.file_uploader(
                "背景音乐 (可选)",
                type=['mp3', 'wav', 'aac'],
                help="为视频添加背景音乐"
            )
            
            if st.button("🎬 创建幻灯片视频", use_container_width=True):
                with st.spinner("正在创建幻灯片视频..."):
                    try:
                        # 保存上传的图片
                        temp_image_paths = []
                        for file in uploaded_files:
                            temp_path = os.path.join("./temp", f"slideshow_{file.name}")
                            with open(temp_path, "wb") as f:
                                f.write(file.read())
                            temp_image_paths.append(temp_path)
                        
                        # 处理背景音乐
                        music_path = None
                        if background_music:
                            music_path = os.path.join("./temp", f"bg_music_{background_music.name}")
                            with open(music_path, "wb") as f:
                                f.write(background_music.read())
                        
                        # 生成视频
                        result = st.session_state.image_to_video.create_slideshow_video(
                            image_paths=temp_image_paths,
                            duration_per_image=duration_per_image,
                            transition_duration=transition_duration,
                            output_size=(output_width, output_height),
                            fps=fps,
                            background_music=music_path
                        )
                        
                        if result:
                            st.success("✅ 幻灯片视频创建成功！")
                            
                            # 显示视频信息
                            metadata = result['metadata']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("总时长", f"{metadata['total_duration']:.1f}秒")
                            with col2:
                                file_size = metadata['file_size'] / (1024 * 1024)
                                st.metric("文件大小", f"{file_size:.1f}MB")
                            with col3:
                                st.metric("图片数量", metadata['image_count'])
                            
                            # 视频预览
                            if os.path.exists(result['video_path']):
                                st.markdown("### 🎥 视频预览")
                                st.video(result['video_path'])
                                
                                # 下载按钮
                                with open(result['video_path'], "rb") as video_file:
                                    st.download_button(
                                        "📥 下载视频",
                                        video_file.read(),
                                        file_name=os.path.basename(result['video_path']),
                                        mime="video/mp4"
                                    )
                        
                        # 清理临时文件
                        for temp_path in temp_image_paths:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        if music_path and os.path.exists(music_path):
                            os.remove(music_path)
                    
                    except Exception as e:
                        st.error(f"❌ 视频创建失败: {str(e)}")
    
    with tab2:
        st.subheader("单图动画视频")
        
        uploaded_file = st.file_uploader(
            "上传单张图片",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="single_image"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="预览图片", use_column_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                animation_type = st.selectbox(
                    "动画效果",
                    ["zoom", "pan", "fade"],
                    format_func=lambda x: {
                        "zoom": "缩放效果",
                        "pan": "平移效果", 
                        "fade": "淡入淡出"
                    }[x]
                )
                
                duration = st.slider("视频时长 (秒)", 3.0, 30.0, 5.0, 1.0)
            
            with col2:
                output_width = st.selectbox("宽度", [1280, 1920, 3840], index=1, key="anim_width")
                output_height = st.selectbox("高度", [720, 1080, 2160], index=1, key="anim_height")
                fps = st.selectbox("帧率", [24, 30, 60], index=1, key="anim_fps")
            
            if st.button("🎬 创建动画视频", use_container_width=True):
                with st.spinner(f"正在创建{animation_type}动画视频..."):
                    try:
                        # 保存上传的图片
                        from PIL import Image
                        image = Image.open(uploaded_file)
                        
                        result = st.session_state.image_to_video.create_animated_video(
                            image_path=image,
                            animation_type=animation_type,
                            duration=duration,
                            output_size=(output_width, output_height),
                            fps=fps
                        )
                        
                        if result:
                            st.success("✅ 动画视频创建成功！")
                            
                            # 显示视频信息
                            metadata = result['metadata']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("时长", f"{metadata['duration']}秒")
                            with col2:
                                file_size = metadata['file_size'] / (1024 * 1024)
                                st.metric("文件大小", f"{file_size:.1f}MB")
                            with col3:
                                st.metric("动画效果", metadata['animation_type'])
                            
                            # 视频预览和下载
                            if os.path.exists(result['video_path']):
                                st.markdown("### 🎥 视频预览")
                                st.video(result['video_path'])
                                
                                with open(result['video_path'], "rb") as video_file:
                                    st.download_button(
                                        "📥 下载视频",
                                        video_file.read(),
                                        file_name=os.path.basename(result['video_path']),
                                        mime="video/mp4",
                                        key="download_animated"
                                    )
                    
                    except Exception as e:
                        st.error(f"❌ 视频创建失败: {str(e)}")
    
    with tab3:
        st.subheader("对比视频")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**对比前图片**")
            before_image = st.file_uploader(
                "上传前图片",
                type=['png', 'jpg', 'jpeg', 'webp'],
                key="before_image"
            )
            if before_image:
                st.image(before_image, caption="对比前", use_column_width=True)
        
        with col2:
            st.markdown("**对比后图片**")
            after_image = st.file_uploader(
                "上传后图片", 
                type=['png', 'jpg', 'jpeg', 'webp'],
                key="after_image"
            )
            if after_image:
                st.image(after_image, caption="对比后", use_column_width=True)
        
        if before_image and after_image:
            comparison_type = st.selectbox(
                "对比方式",
                ["side_by_side", "transition", "before_after"],
                format_func=lambda x: {
                    "side_by_side": "并排对比",
                    "transition": "转场对比",
                    "before_after": "前后对比"
                }[x]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                duration = st.slider("视频总时长 (秒)", 5.0, 30.0, 10.0, 1.0, key="comp_duration")
            with col2:
                transition_point = st.slider(
                    "转场时间点 (秒)", 
                    1.0, duration-1.0, duration/2, 0.5,
                    disabled=comparison_type != "transition",
                    help="仅在转场对比模式下有效"
                )
            
            if st.button("🎬 创建对比视频", use_container_width=True):
                with st.spinner("正在创建对比视频..."):
                    try:
                        from PIL import Image
                        before_img = Image.open(before_image)
                        after_img = Image.open(after_image)
                        
                        result = st.session_state.image_to_video.create_comparison_video(
                            before_image=before_img,
                            after_image=after_img,
                            comparison_type=comparison_type,
                            duration=duration,
                            transition_point=transition_point if comparison_type == "transition" else None
                        )
                        
                        if result:
                            st.success("✅ 对比视频创建成功！")
                            
                            if os.path.exists(result['video_path']):
                                st.markdown("### 🎥 视频预览")
                                st.video(result['video_path'])
                                
                                with open(result['video_path'], "rb") as video_file:
                                    st.download_button(
                                        "📥 下载视频",
                                        video_file.read(),
                                        file_name=os.path.basename(result['video_path']),
                                        mime="video/mp4",
                                        key="download_comparison"
                                    )
                    
                    except Exception as e:
                        st.error(f"❌ 视频创建失败: {str(e)}")

def show_image_editing():
    """图像编辑页面"""
    st.header("🖼️ 智能图像编辑")
    
    if not IMAGE_GENERATION_AVAILABLE:
        st.error("""
        ❌ 图像编辑功能不可用
        
        请安装图像编辑依赖：
        ```bash
        pip install -r requirements-image.txt
        ```
        
        注意：首次使用需要下载Qwen-Image-Edit模型，请确保有足够的存储空间和网络带宽。
        """)
        return
    
    st.markdown("""
    使用Qwen-Image-Edit进行智能图像编辑，支持视角转换、风格变换、环境改变等。
    上传图片并输入编辑指令，AI将为您智能编辑图像。
    """)
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "上传需要编辑的图片",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="支持常见的图片格式"
    )
    
    if uploaded_file is not None:
        # 显示原图
        st.subheader("📸 原始图片")
        original_image = Image.open(uploaded_file)
        st.image(original_image, caption="原始图片", use_column_width=True)
        
        # 编辑选项
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
            "🎯 自由编辑", 
            "👁️ 视角转换", 
            "🎨 风格变换", 
            "🌍 环境变换", 
            "🔧 对象变换",
            "👤 虚拟形象",
            "🗑️ AI消除",
            "🎨 AI重绘", 
            "🌍 虚拟场景",
            "👗 穿搭模拟",
            "📝 文字海报"
        ])
        
        with tab1:
            st.subheader("自由编辑模式")
            
            with st.form("free_edit_form"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    edit_prompt = st.text_area(
                        "编辑指令 *",
                        height=100,
                        placeholder="例如: 把兔子的颜色改成紫色，添加闪光背景",
                        help="描述您希望对图片进行的编辑"
                    )
                    
                    negative_prompt = st.text_area(
                        "负面提示词 (可选)",
                        height=60,
                        placeholder="不希望出现的内容",
                        help="描述不希望在编辑后图片中出现的元素"
                    )
                
                with col2:
                    true_cfg_scale = st.slider(
                        "编辑强度",
                        1.0, 10.0, 4.0, 0.5,
                        help="控制编辑效果的强度"
                    )
                    
                    num_inference_steps = st.slider(
                        "推理步数",
                        20, 100, 50, 5,
                        help="更多步数通常带来更好的质量"
                    )
                    
                    seed = st.number_input(
                        "随机种子 (可选)",
                        min_value=0, max_value=2**32-1, value=0,
                        help="设置为0使用随机种子"
                    )
                    
                    optimize_prompt = st.checkbox(
                        "优化提示词",
                        value=True,
                        help="使用AI优化您的编辑指令"
                    )
                
                submitted = st.form_submit_button("🖼️ 开始编辑", use_container_width=True)
            
            if submitted and edit_prompt:
                with st.spinner("正在编辑图像，请稍候..."):
                    try:
                        result = st.session_state.image_editor.edit_image(
                            image=original_image,
                            edit_prompt=edit_prompt,
                            negative_prompt=negative_prompt,
                            true_cfg_scale=true_cfg_scale,
                            num_inference_steps=num_inference_steps,
                            seed=seed if seed > 0 else None,
                            optimize_prompt=optimize_prompt
                        )
                        
                        if result:
                            st.success("✅ 图像编辑成功！")
                            
                            # 显示编辑结果
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**编辑前**")
                                st.image(result['original_image'], use_column_width=True)
                            
                            with col2:
                                st.markdown("**编辑后**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 显示编辑信息
                            with st.expander("📊 编辑信息"):
                                metadata = result['metadata']
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("编辑强度", metadata['true_cfg_scale'])
                                    st.metric("推理步数", metadata['num_inference_steps'])
                                
                                with col2:
                                    st.metric("随机种子", metadata['seed'])
                                    st.text(f"原图尺寸: {metadata['original_size']}")
                                
                                with col3:
                                    st.text(f"编辑时间: {metadata['edited_at'][:19]}")
                                    st.text(f"编辑后尺寸: {metadata['edited_size']}")
                                
                                st.text_area("编辑指令", metadata['edit_prompt'], height=60, key="edit_info")
                            
                            # 下载选项
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载编辑后的图片",
                                data=img_bytes,
                                file_name=f"edited_{uploaded_file.name}",
                                mime="image/png"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 编辑失败: {str(e)}")
                        if "memory" in str(e).lower():
                            st.info("💡 提示：如果遇到显存不足错误，可以尝试减少推理步数")
            
            elif submitted:
                st.warning("⚠️ 请输入编辑指令")
        
        with tab2:
            st.subheader("视角转换")
            
            # 获取可用的视角选项
            perspective_options = [
                "从正面看", "从侧面看", "从背面看",
                "从上往下看", "从下往上看", "俯视图", "仰视图"
            ]
            
            selected_perspective = st.selectbox(
                "选择目标视角",
                perspective_options,
                help="选择您希望转换到的视角"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("编辑强度", 1.0, 10.0, 4.0, 0.5, key="perspective_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="perspective_steps")
            
            if st.button("🔄 执行视角转换", use_container_width=True):
                with st.spinner(f"正在转换视角到'{selected_perspective}'..."):
                    try:
                        result = st.session_state.image_editor.perspective_transform(
                            image=original_image,
                            target_view=selected_perspective,
                            true_cfg_scale=cfg_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ 视角转换成功！")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**转换前**")
                                st.image(result['original_image'], use_column_width=True)
                            with col2:
                                st.markdown("**转换后**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载转换后的图片",
                                data=img_bytes,
                                file_name=f"perspective_{selected_perspective}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_perspective"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 视角转换失败: {str(e)}")
        
        with tab3:
            st.subheader("风格变换")
            
            style_options = [
                "油画风格", "水彩风格", "素描风格", "动漫风格",
                "照片风格", "印象派", "抽象艺术"
            ]
            
            selected_style = st.selectbox(
                "选择目标风格",
                style_options,
                help="选择您希望转换到的艺术风格"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("转换强度", 1.0, 10.0, 4.0, 0.5, key="style_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="style_steps")
            
            if st.button("🎨 执行风格变换", use_container_width=True):
                with st.spinner(f"正在转换风格到'{selected_style}'..."):
                    try:
                        result = st.session_state.image_editor.style_transform(
                            image=original_image,
                            target_style=selected_style,
                            true_cfg_scale=cfg_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ 风格变换成功！")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**变换前**")
                                st.image(result['original_image'], use_column_width=True)
                            with col2:
                                st.markdown("**变换后**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载变换后的图片",
                                data=img_bytes,
                                file_name=f"style_{selected_style}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_style"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 风格变换失败: {str(e)}")
        
        with tab4:
            st.subheader("环境变换")
            
            env_options = [
                "白天转夜晚", "夜晚转白天", "晴天转雨天",
                "室内转室外", "现代转古代", "城市转乡村", "春天转秋天"
            ]
            
            selected_env = st.selectbox(
                "选择环境变换",
                env_options,
                help="选择您希望的环境变换类型"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("变换强度", 1.0, 10.0, 4.0, 0.5, key="env_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="env_steps")
            
            if st.button("🌍 执行环境变换", use_container_width=True):
                with st.spinner(f"正在执行'{selected_env}'变换..."):
                    try:
                        result = st.session_state.image_editor.environment_transform(
                            image=original_image,
                            target_environment=selected_env,
                            true_cfg_scale=cfg_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ 环境变换成功！")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**变换前**")
                                st.image(result['original_image'], use_column_width=True)
                            with col2:
                                st.markdown("**变换后**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载变换后的图片",
                                data=img_bytes,
                                file_name=f"env_{selected_env}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_env"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 环境变换失败: {str(e)}")
        
        with tab5:
            st.subheader("对象变换")
            
            transform_types = [
                "改变颜色", "改变材质", "改变大小", "添加装饰",
                "改变表情", "改变姿态", "改变服装"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                transform_type = st.selectbox(
                    "变换类型",
                    transform_types,
                    help="选择要变换的对象属性"
                )
            
            with col2:
                transform_value = st.text_input(
                    "变换目标",
                    placeholder="例如: 红色、金属、巨大、花朵装饰等",
                    help="描述变换的目标值"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("变换强度", 1.0, 10.0, 4.0, 0.5, key="obj_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="obj_steps")
            
            if st.button("🔧 执行对象变换", use_container_width=True):
                if not transform_value:
                    st.warning("⚠️ 请输入变换目标")
                else:
                    with st.spinner(f"正在执行'{transform_type}'到'{transform_value}'..."):
                        try:
                            result = st.session_state.image_editor.object_transform(
                                image=original_image,
                                transform_type=transform_type,
                                transform_value=transform_value,
                                true_cfg_scale=cfg_scale,
                                num_inference_steps=steps
                            )
                            
                            if result:
                                st.success("✅ 对象变换成功！")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**变换前**")
                                    st.image(result['original_image'], use_column_width=True)
                                with col2:
                                    st.markdown("**变换后**")
                                    st.image(result['edited_image'], use_column_width=True)
                                
                                # 下载按钮
                                img_bytes = io.BytesIO()
                                result['edited_image'].save(img_bytes, format='PNG')
                                img_bytes = img_bytes.getvalue()
                                
                                st.download_button(
                                    "📥 下载变换后的图片",
                                    data=img_bytes,
                                    file_name=f"obj_{transform_type}_{transform_value}_{uploaded_file.name}",
                                    mime="image/png",
                                    key="download_obj"
                                )
                        
                        except Exception as e:
                            st.error(f"❌ 对象变换失败: {str(e)}")
        
        # 新增功能标签页
        with tab6:
            st.subheader("👤 虚拟形象生成")
            st.markdown("生成各种风格的虚拟人物形象")
            
            avatar_types = [
                "生成3D虚拟人", "卡通角色", "动漫人物", 
                "游戏角色", "商务形象", "时尚模特"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                avatar_type = st.selectbox(
                    "形象类型",
                    avatar_types,
                    help="选择要生成的虚拟形象类型"
                )
            
            with col2:
                description = st.text_area(
                    "详细描述",
                    placeholder="例如: 长发女性，蓝色眼睛，微笑表情，现代服装",
                    help="描述虚拟形象的具体特征"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("生成强度", 1.0, 10.0, 4.0, 0.5, key="avatar_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="avatar_steps")
            
            if st.button("👤 生成虚拟形象", use_container_width=True):
                with st.spinner(f"正在生成{avatar_type}..."):
                    try:
                        result = st.session_state.image_editor.generate_avatar(
                            avatar_type=avatar_type,
                            description=description,
                            true_cfg_scale=cfg_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ 虚拟形象生成成功！")
                            st.image(result['edited_image'], caption="生成的虚拟形象", use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载虚拟形象",
                                data=img_bytes,
                                file_name=f"avatar_{avatar_type}_{int(time.time())}.png",
                                mime="image/png",
                                key="download_avatar"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 虚拟形象生成失败: {str(e)}")
        
        with tab7:
            st.subheader("🗑️ AI消除功能")
            st.markdown("智能移除图像中的对象、水印、背景等")
            
            remove_types = [
                "移除对象", "消除水印", "清除背景", 
                "去除文字", "消除瑕疵", "删除人物"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                remove_type = st.selectbox(
                    "消除类型",
                    remove_types,
                    help="选择要消除的内容类型"
                )
            
            with col2:
                target_object = st.text_input(
                    "目标对象",
                    placeholder="例如: 汽车、文字、人物等（可选）",
                    help="具体描述要移除的对象"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                guidance_scale = st.slider("消除强度", 1.0, 20.0, 7.5, 0.5, key="remove_guidance")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="remove_steps")
            
            if st.button("🗑️ 执行AI消除", use_container_width=True):
                with st.spinner(f"正在执行{remove_type}..."):
                    try:
                        result = st.session_state.image_editor.ai_remove(
                            image=original_image,
                            remove_type=remove_type,
                            target_object=target_object,
                            guidance_scale=guidance_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ AI消除成功！")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**消除前**")
                                st.image(result['original_image'], use_column_width=True)
                            with col2:
                                st.markdown("**消除后**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载消除后的图片",
                                data=img_bytes,
                                file_name=f"removed_{remove_type}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_remove"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ AI消除失败: {str(e)}")
        
        with tab8:
            st.subheader("🎨 AI重绘功能")
            st.markdown("重新绘制图像的局部或整体内容")
            
            redraw_types = [
                "局部重绘", "背景重绘", "人物重绘", 
                "物体重绘", "全图重绘", "细节重绘"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                redraw_type = st.selectbox(
                    "重绘类型",
                    redraw_types,
                    help="选择重绘的范围和类型"
                )
            
            with col2:
                description = st.text_area(
                    "重绘描述",
                    placeholder="例如: 改为森林背景、变成卡通风格、添加阳光效果等",
                    help="描述重绘后的效果"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("重绘强度", 1.0, 10.0, 4.0, 0.5, key="redraw_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="redraw_steps")
            
            if st.button("🎨 执行AI重绘", use_container_width=True):
                if not description:
                    st.warning("⚠️ 请输入重绘描述")
                else:
                    with st.spinner(f"正在执行{redraw_type}..."):
                        try:
                            result = st.session_state.image_editor.ai_redraw(
                                image=original_image,
                                redraw_type=redraw_type,
                                description=description,
                                true_cfg_scale=cfg_scale,
                                num_inference_steps=steps
                            )
                            
                            if result:
                                st.success("✅ AI重绘成功！")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**重绘前**")
                                    st.image(result['original_image'], use_column_width=True)
                                with col2:
                                    st.markdown("**重绘后**")
                                    st.image(result['edited_image'], use_column_width=True)
                                
                                # 下载按钮
                                img_bytes = io.BytesIO()
                                result['edited_image'].save(img_bytes, format='PNG')
                                img_bytes = img_bytes.getvalue()
                                
                                st.download_button(
                                    "📥 下载重绘后的图片",
                                    data=img_bytes,
                                    file_name=f"redrawn_{redraw_type}_{uploaded_file.name}",
                                    mime="image/png",
                                    key="download_redraw"
                                )
                        
                        except Exception as e:
                            st.error(f"❌ AI重绘失败: {str(e)}")
        
        with tab9:
            st.subheader("🌍 虚拟场景生成")
            st.markdown("将图像转换到不同的虚拟场景环境")
            
            scene_types = [
                "科幻场景", "奇幻世界", "历史场景", 
                "自然风光", "城市场景", "室内空间"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                scene_type = st.selectbox(
                    "场景类型",
                    scene_types,
                    help="选择要生成的虚拟场景类型"
                )
            
            with col2:
                scene_elements = st.text_input(
                    "场景元素",
                    placeholder="例如: 星际飞船、魔法森林、古代城堡等",
                    help="描述场景的具体元素和特征"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("场景强度", 1.0, 10.0, 4.0, 0.5, key="scene_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="scene_steps")
            
            if st.button("🌍 生成虚拟场景", use_container_width=True):
                with st.spinner(f"正在生成{scene_type}..."):
                    try:
                        result = st.session_state.image_editor.virtual_scene(
                            image=original_image,
                            scene_type=scene_type,
                            scene_elements=scene_elements,
                            true_cfg_scale=cfg_scale,
                            num_inference_steps=steps
                        )
                        
                        if result:
                            st.success("✅ 虚拟场景生成成功！")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**原始场景**")
                                st.image(result['original_image'], use_column_width=True)
                            with col2:
                                st.markdown("**虚拟场景**")
                                st.image(result['edited_image'], use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载虚拟场景",
                                data=img_bytes,
                                file_name=f"scene_{scene_type}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_scene"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 虚拟场景生成失败: {str(e)}")
        
        with tab10:
            st.subheader("👗 穿搭模拟功能")
            st.markdown("模拟不同的服装搭配和风格效果")
            
            outfit_types = [
                "换装试衣", "配饰搭配", "发型变换", 
                "妆容调整", "颜色搭配", "季节穿搭"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                outfit_type = st.selectbox(
                    "穿搭类型",
                    outfit_types,
                    help="选择穿搭模拟的类型"
                )
            
            with col2:
                outfit_details = st.text_area(
                    "穿搭详情",
                    placeholder="例如: 正装西服、休闲T恤、波西米亚长裙等",
                    help="描述具体的穿搭风格和细节"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cfg_scale = st.slider("穿搭强度", 1.0, 10.0, 4.0, 0.5, key="outfit_cfg")
            with col2:
                steps = st.slider("推理步数", 20, 100, 50, 5, key="outfit_steps")
            
            if st.button("👗 执行穿搭模拟", use_container_width=True):
                if not outfit_details:
                    st.warning("⚠️ 请输入穿搭详情")
                else:
                    with st.spinner(f"正在模拟{outfit_type}..."):
                        try:
                            result = st.session_state.image_editor.outfit_simulation(
                                image=original_image,
                                outfit_type=outfit_type,
                                outfit_details=outfit_details,
                                true_cfg_scale=cfg_scale,
                                num_inference_steps=steps
                            )
                            
                            if result:
                                st.success("✅ 穿搭模拟成功！")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**穿搭前**")
                                    st.image(result['original_image'], use_column_width=True)
                                with col2:
                                    st.markdown("**穿搭后**")
                                    st.image(result['edited_image'], use_column_width=True)
                                
                                # 下载按钮
                                img_bytes = io.BytesIO()
                                result['edited_image'].save(img_bytes, format='PNG')
                                img_bytes = img_bytes.getvalue()
                                
                                st.download_button(
                                    "📥 下载穿搭效果",
                                    data=img_bytes,
                                    file_name=f"outfit_{outfit_type}_{uploaded_file.name}",
                                    mime="image/png",
                                    key="download_outfit"
                                )
                        
                        except Exception as e:
                            st.error(f"❌ 穿搭模拟失败: {str(e)}")
        
        with tab11:
            st.subheader("📝 文字设计与海报编辑")
            st.markdown("添加艺术文字和设计各种风格的海报")
            
            # 文字设计区域
            st.markdown("#### 🔤 文字设计")
            
            text_types = [
                "艺术字体", "标题设计", "logo设计", 
                "书法字体", "立体文字", "霓虹文字"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                text_type = st.selectbox(
                    "文字类型",
                    text_types,
                    help="选择文字设计的类型"
                )
            
            with col2:
                text_content = st.text_input(
                    "文字内容",
                    placeholder="输入要添加的文字",
                    help="输入需要设计的文字内容"
                )
            
            font_style = st.text_input(
                "字体风格",
                placeholder="例如: 现代简约、古典优雅、科技感等",
                help="描述文字的设计风格"
            )
            
            if st.button("📝 添加文字设计", use_container_width=True):
                if not text_content:
                    st.warning("⚠️ 请输入文字内容")
                else:
                    with st.spinner(f"正在添加{text_type}文字..."):
                        try:
                            result = st.session_state.image_editor.text_design(
                                image=original_image,
                                text_type=text_type,
                                text_content=text_content,
                                font_style=font_style or "modern"
                            )
                            
                            if result:
                                st.success("✅ 文字设计成功！")
                                st.image(result['edited_image'], caption="添加文字后的效果", use_column_width=True)
                                
                                # 下载按钮
                                img_bytes = io.BytesIO()
                                result['edited_image'].save(img_bytes, format='PNG')
                                img_bytes = img_bytes.getvalue()
                                
                                st.download_button(
                                    "📥 下载文字设计",
                                    data=img_bytes,
                                    file_name=f"text_{text_type}_{uploaded_file.name}",
                                    mime="image/png",
                                    key="download_text"
                                )
                        
                        except Exception as e:
                            st.error(f"❌ 文字设计失败: {str(e)}")
            
            st.divider()
            
            # 海报设计区域
            st.markdown("#### 🎪 海报编辑")
            
            poster_types = [
                "电影海报", "音乐海报", "活动海报", 
                "产品海报", "复古海报", "简约海报"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                poster_type = st.selectbox(
                    "海报类型",
                    poster_types,
                    help="选择海报设计的类型"
                )
            
            with col2:
                theme = st.text_input(
                    "海报主题",
                    placeholder="例如: 科幻、浪漫、商务、艺术等",
                    help="描述海报的主题和风格"
                )
            
            if st.button("🎪 设计海报", use_container_width=True):
                with st.spinner(f"正在设计{poster_type}..."):
                    try:
                        result = st.session_state.image_editor.poster_design(
                            image=original_image,
                            poster_type=poster_type,
                            theme=theme
                        )
                        
                        if result:
                            st.success("✅ 海报设计成功！")
                            st.image(result['edited_image'], caption="海报设计效果", use_column_width=True)
                            
                            # 下载按钮
                            img_bytes = io.BytesIO()
                            result['edited_image'].save(img_bytes, format='PNG')
                            img_bytes = img_bytes.getvalue()
                            
                            st.download_button(
                                "📥 下载海报设计",
                                data=img_bytes,
                                file_name=f"poster_{poster_type}_{uploaded_file.name}",
                                mime="image/png",
                                key="download_poster"
                            )
                    
                    except Exception as e:
                        st.error(f"❌ 海报设计失败: {str(e)}")

if __name__ == "__main__":
    main()