"""
Web界面工具函数
提供Streamlit应用的辅助功能
"""

import streamlit as st
import os
from datetime import datetime
from typing import Dict, Any

def display_system_info():
    """显示系统信息侧边栏"""
    st.sidebar.markdown("### 🔧 系统状态")
    
    # API状态检查
    api_status = check_api_keys()
    for provider, status in api_status.items():
        icon = "✅" if status else "❌"
        st.sidebar.markdown(f"{provider}: {icon}")
    
    # 功能状态检查
    st.sidebar.markdown("### 📦 功能模块")
    
    # 视频生成状态
    try:
        from src.video_generation.video_generator import VideoGenerator
        st.sidebar.markdown("视频生成: ✅")
    except ImportError:
        st.sidebar.markdown("视频生成: ❌")
        with st.sidebar.expander("安装视频功能"):
            st.code("pip install -r requirements-video.txt")
    
    # Whisper状态
    try:
        import whisper
        st.sidebar.markdown("语音识别: ✅")
    except ImportError:
        st.sidebar.markdown("语音识别: ❌")

def check_api_keys():
    """检查API密钥配置状态"""
    return {
        "DeepSeek": bool(os.getenv('DEEPSEEK_API_KEY')),
        "OpenAI": bool(os.getenv('OPENAI_API_KEY')),
        "Anthropic": bool(os.getenv('ANTHROPIC_API_KEY'))
    }

def show_feature_card(title: str, description: str, icon: str = "📝"):
    """显示功能卡片"""
    st.markdown(f"""
    <div class="feature-card">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def show_success_message(message: str):
    """显示成功消息"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message: str):
    """显示错误消息"""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def display_progress_bar(progress: float, text: str = ""):
    """显示进度条"""
    progress_bar = st.progress(progress)
    if text:
        st.text(text)
    return progress_bar

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def display_metadata(metadata: Dict[str, Any], title: str = "元数据"):
    """显示元数据信息"""
    with st.expander(f"📊 {title}"):
        for key, value in metadata.items():
            if key.endswith('_at') and isinstance(value, str):
                # 格式化时间戳
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    value = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            st.text(f"{key}: {value}")

def create_download_button(content: str, filename: str, mime_type: str = "text/plain", label: str = "下载"):
    """创建下载按钮"""
    st.download_button(
        label=f"📥 {label}",
        data=content,
        file_name=filename,
        mime=mime_type,
        use_container_width=True
    )

def display_usage_stats():
    """显示使用统计"""
    col1, col2, col3 = st.columns(3)
    
    # 这里可以添加实际的统计数据
    with col1:
        st.metric("今日使用", "0", delta="0")
    
    with col2:
        st.metric("本月使用", "0", delta="0")
    
    with col3:
        st.metric("总使用次数", "0", delta="0")

def show_help_section():
    """显示帮助信息"""
    with st.expander("❓ 使用帮助"):
        st.markdown("""
        ## 📚 快速入门
        
        ### 1. 配置API密钥
        - 复制 `.env.example` 为 `.env`
        - 填入您的API密钥
        - 推荐使用DeepSeek（成本较低）
        
        ### 2. 功能说明
        - **文章写作**: 生成各种风格的文章内容
        - **小说创作**: 创作章节和故事大纲
        - **语音识别**: 上传音频文件进行转录和摘要
        - **视频生成**: 根据文本生成视频内容（需要安装额外依赖）
        - **提示词优化**: 分析和改进您的AI提示词
        
        ### 3. 注意事项
        - 较大的音频文件可能需要较长处理时间
        - 视频生成功能需要安装额外依赖包
        - 建议在稳定的网络环境下使用
        
        ### 4. 故障排除
        如遇到问题，请检查：
        - API密钥是否正确配置
        - 网络连接是否正常
        - 依赖包是否完整安装
        """)

def custom_css():
    """添加自定义CSS样式"""
    st.markdown("""
    <style>
        /* 主标题样式 */
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 功能卡片样式 */
        .feature-card {
            background: linear-gradient(135deg, #f0f2f6 0%, #e8ebf0 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border-left: 4px solid #1f77b4;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
        }
        
        /* 成功消息样式 */
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid #c3e6cb;
        }
        
        /* 错误消息样式 */
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid #f5c6cb;
        }
        
        /* 侧边栏样式 */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* 按钮悬停效果 */
        .stButton > button {
            background: linear-gradient(90deg, #1f77b4 0%, #17a2b8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* 文本区域样式 */
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 2px solid #e9ecef;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: #1f77b4;
            box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25);
        }
        
        /* 指标卡片样式 */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        /* 加载动画 */
        .loading-animation {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #1f77b4;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .main-header {
                font-size: 2rem;
            }
            
            .feature-card {
                padding: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)