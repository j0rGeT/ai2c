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

# 初始化session state
if 'content_generator' not in st.session_state:
    st.session_state.content_generator = ContentGenerator()
if 'speech_processor' not in st.session_state:
    st.session_state.speech_processor = SpeechProcessor()
if 'prompt_optimizer' not in st.session_state:
    st.session_state.prompt_optimizer = PromptOptimizer()
if VIDEO_GENERATION_AVAILABLE and 'video_generator' not in st.session_state:
    st.session_state.video_generator = VideoGenerator()

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
        st.metric("支持的文件格式", "10+")
        st.metric("功能模块", "5个")
        st.metric("支持语言", "中英文")
        
        st.markdown("### 🔗 快速链接")
        if st.button("📝 开始写作", use_container_width=True):
            st.session_state.page = "📝 文章写作"
            st.rerun()
        if st.button("🎤 处理音频", use_container_width=True):
            st.session_state.page = "🎤 语音识别"
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

if __name__ == "__main__":
    main()