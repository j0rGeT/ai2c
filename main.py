#!/usr/bin/env python3
"""
AI内容创作系统 - 主程序
支持文章写作、语音识别、视频生成、提示词优化等功能
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, Any

from src.content_generation.content_generator import ContentGenerator
from src.speech_recognition.speech_processor import SpeechProcessor
from src.prompt_optimization.prompt_optimizer import PromptOptimizer

# 视频生成器的可选导入
try:
    from src.video_generation.video_generator import VideoGenerator
    VIDEO_GENERATION_AVAILABLE = True
except ImportError:
    VIDEO_GENERATION_AVAILABLE = False
    VideoGenerator = None

# 图像生成器的可选导入
try:
    from src.image_generation.text_to_image import TextToImageGenerator
    from src.image_generation.image_to_video import ImageToVideoGenerator
    from src.image_generation.image_editor import ImageEditor
    IMAGE_GENERATION_AVAILABLE = True
except ImportError:
    IMAGE_GENERATION_AVAILABLE = False
    TextToImageGenerator = None
    ImageToVideoGenerator = None
    ImageEditor = None

class AI2CSystem:
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.speech_processor = SpeechProcessor()
        self.prompt_optimizer = PromptOptimizer()
        
        # 视频生成器的可选初始化
        if VIDEO_GENERATION_AVAILABLE:
            self.video_generator = VideoGenerator()
        else:
            self.video_generator = None
        
        # 图像生成器的可选初始化
        if IMAGE_GENERATION_AVAILABLE:
            self.text_to_image = TextToImageGenerator()
            self.image_to_video = ImageToVideoGenerator()
            self.image_editor = ImageEditor()
        else:
            self.text_to_image = None
            self.image_to_video = None
            self.image_editor = None
    
    def generate_article(self, topic: str, style: str = "informative", length: str = "medium", provider: str = None):
        print(f"正在生成关于'{topic}'的文章...")
        
        try:
            result = self.content_generator.generate_article(topic, style, length, provider)
            filepath = self.content_generator.save_content(result)
            
            print(f"✅ 文章生成成功!")
            print(f"📄 文件保存至: {filepath}")
            print(f"📊 字数统计: {result['metadata']['word_count']} 字")
            
            return result
        except Exception as e:
            print(f"❌ 文章生成失败: {str(e)}")
            return None
    
    def generate_novel_chapter(self, plot: str, characters: str = "", setting: str = "", chapter_number: int = 1, provider: str = None):
        print(f"正在生成第{chapter_number}章小说...")
        
        try:
            result = self.content_generator.generate_novel_chapter(plot, characters, setting, chapter_number, provider)
            filepath = self.content_generator.save_content(result)
            
            print(f"✅ 小说章节生成成功!")
            print(f"📄 文件保存至: {filepath}")
            print(f"📊 字数统计: {result['metadata']['word_count']} 字")
            
            return result
        except Exception as e:
            print(f"❌ 小说生成失败: {str(e)}")
            return None
    
    def generate_story_outline(self, theme: str, genre: str = "现代", length: str = "中篇", provider: str = None):
        print(f"正在生成'{theme}'小说大纲...")
        
        try:
            result = self.content_generator.generate_story_outline(theme, genre, length, provider)
            filepath = self.content_generator.save_content(result)
            
            print(f"✅ 小说大纲生成成功!")
            print(f"📄 文件保存至: {filepath}")
            
            return result
        except Exception as e:
            print(f"❌ 大纲生成失败: {str(e)}")
            return None
    
    def process_audio(self, audio_path: str, language: str = "zh", summary_type: str = "详细"):
        if not os.path.exists(audio_path):
            print(f"❌ 音频文件不存在: {audio_path}")
            return None
        
        print(f"正在处理音频文件: {os.path.basename(audio_path)}")
        
        try:
            result = self.speech_processor.transcribe_and_summarize(
                audio_path, language, summary_type
            )
            filepath = self.speech_processor.save_results(result)
            
            duration = result['metadata']['duration']
            print(f"✅ 音频处理完成!")
            print(f"📄 转录文件保存至: {filepath}")
            print(f"⏱️ 音频时长: {duration:.1f} 秒")
            print(f"🔤 识别语言: {result['transcription']['language']}")
            
            return result
        except Exception as e:
            print(f"❌ 音频处理失败: {str(e)}")
            return None
    
    def generate_video(self, text_prompt: str, video_style: str = "教育", duration: int = 30, output_type: str = "text_video"):
        if not VIDEO_GENERATION_AVAILABLE or not self.video_generator:
            print("❌ 视频生成功能不可用")
            print("💡 请安装视频生成依赖: pip install -r requirements-video.txt")
            return None
            
        print(f"正在生成视频: {text_prompt[:30]}...")
        
        try:
            result = self.video_generator.generate_video_from_text(
                text_prompt, video_style, duration, output_type
            )
            
            file_size = result['metadata']['file_size'] / (1024 * 1024)  # MB
            print(f"✅ 视频生成成功!")
            print(f"🎥 视频保存至: {result['video_path']}")
            print(f"⏱️ 视频时长: {duration} 秒")
            print(f"💾 文件大小: {file_size:.1f} MB")
            
            self.video_generator.cleanup_temp_files()
            return result
        except Exception as e:
            print(f"❌ 视频生成失败: {str(e)}")
            return None
    
    def optimize_prompt(self, original_prompt: str, optimization_goal: str = "全面优化", target_domain: str = "通用"):
        print(f"正在优化提示词...")
        
        try:
            analysis = self.prompt_optimizer.analyze_prompt(original_prompt)
            optimization = self.prompt_optimizer.optimize_prompt(original_prompt, optimization_goal, target_domain)
            
            print(f"✅ 提示词优化完成!")
            print(f"📊 原始提示词长度: {len(original_prompt)} 字符")
            
            if 'scores' in analysis:
                avg_score = sum(analysis['scores'].values()) / len(analysis['scores'])
                print(f"📈 分析评分: {avg_score:.1f}/10")
            
            return {
                "analysis": analysis,
                "optimization": optimization
            }
        except Exception as e:
            print(f"❌ 提示词优化失败: {str(e)}")
            return None
    
    def generate_image(self, prompt: str, style: str = "写实", width: int = 512, height: int = 512, num_images: int = 1):
        if not IMAGE_GENERATION_AVAILABLE or not self.text_to_image:
            print("❌ 图像生成功能不可用")
            print("💡 请安装图像生成依赖: pip install -r requirements-image.txt")
            return None
        
        print(f"正在生成图像: {prompt[:30]}...")
        
        try:
            result = self.text_to_image.generate_image(
                prompt=prompt,
                style=style,
                width=width,
                height=height,
                num_images=num_images
            )
            
            if result:
                print(f"✅ 图像生成成功!")
                print(f"🖼️ 生成数量: {len(result['images'])}")
                print(f"📏 尺寸: {result['metadata']['width']}x{result['metadata']['height']}")
                print(f"🎭 风格: {result['metadata']['style']}")
                print(f"📁 保存路径: {result['saved_paths']}")
            
            return result
        except Exception as e:
            print(f"❌ 图像生成失败: {str(e)}")
            return None
    
    def create_slideshow_video(self, image_paths: list, duration_per_image: float = 3.0):
        if not (IMAGE_GENERATION_AVAILABLE and VIDEO_GENERATION_AVAILABLE):
            print("❌ 图片转视频功能不可用")
            print("💡 请安装依赖: pip install -r requirements-image.txt requirements-video.txt")
            return None
        
        if not self.image_to_video:
            print("❌ 图片转视频模块未初始化")
            return None
        
        print(f"正在创建幻灯片视频，图片数量: {len(image_paths)}")
        
        try:
            result = self.image_to_video.create_slideshow_video(
                image_paths=image_paths,
                duration_per_image=duration_per_image
            )
            
            if result:
                file_size = result['metadata']['file_size'] / (1024 * 1024)
                print(f"✅ 幻灯片视频创建成功!")
                print(f"🎥 视频保存至: {result['video_path']}")
                print(f"⏱️ 总时长: {result['metadata']['total_duration']}秒")
                print(f"💾 文件大小: {file_size:.1f} MB")
            
            return result
        except Exception as e:
            print(f"❌ 视频创建失败: {str(e)}")
            return None
    
    def edit_image(self, image_path: str, edit_prompt: str):
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在编辑图像: {os.path.basename(image_path)}")
        
        try:
            result = self.image_editor.edit_image(
                image=image_path,
                edit_prompt=edit_prompt
            )
            
            if result:
                print(f"✅ 图像编辑成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 编辑后保存至: {result['output_path']}")
                print(f"🎯 编辑指令: {result['metadata']['edit_prompt']}")
            
            return result
        except Exception as e:
            print(f"❌ 图像编辑失败: {str(e)}")
            return None
    
    def generate_avatar(self, avatar_type: str, description: str = ""):
        """生成虚拟形象"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        print(f"正在生成虚拟形象: {avatar_type}")
        
        try:
            result = self.image_editor.generate_avatar(
                avatar_type=avatar_type,
                description=description
            )
            
            if result:
                print(f"✅ 虚拟形象生成成功!")
                print(f"📁 保存至: {result['output_path']}")
                print(f"👤 形象类型: {avatar_type}")
                if description:
                    print(f"📝 描述: {description}")
            
            return result
        except Exception as e:
            print(f"❌ 虚拟形象生成失败: {str(e)}")
            return None
    
    def ai_remove_object(self, image_path: str, remove_type: str, target_object: str = ""):
        """AI消除功能"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在执行AI消除: {remove_type}")
        if target_object:
            print(f"目标对象: {target_object}")
        
        try:
            result = self.image_editor.ai_remove(
                image=image_path,
                remove_type=remove_type,
                target_object=target_object
            )
            
            if result:
                print(f"✅ AI消除成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 保存至: {result['output_path']}")
            
            return result
        except Exception as e:
            print(f"❌ AI消除失败: {str(e)}")
            return None
    
    def ai_redraw_area(self, image_path: str, redraw_type: str, description: str):
        """AI重绘功能"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在执行AI重绘: {redraw_type}")
        print(f"重绘描述: {description}")
        
        try:
            result = self.image_editor.ai_redraw(
                image=image_path,
                redraw_type=redraw_type,
                description=description
            )
            
            if result:
                print(f"✅ AI重绘成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 保存至: {result['output_path']}")
            
            return result
        except Exception as e:
            print(f"❌ AI重绘失败: {str(e)}")
            return None
    
    def create_virtual_scene(self, image_path: str, scene_type: str, scene_elements: str = ""):
        """虚拟场景生成"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在生成虚拟场景: {scene_type}")
        if scene_elements:
            print(f"场景元素: {scene_elements}")
        
        try:
            result = self.image_editor.virtual_scene(
                image=image_path,
                scene_type=scene_type,
                scene_elements=scene_elements
            )
            
            if result:
                print(f"✅ 虚拟场景生成成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 保存至: {result['output_path']}")
            
            return result
        except Exception as e:
            print(f"❌ 虚拟场景生成失败: {str(e)}")
            return None
    
    def simulate_outfit(self, image_path: str, outfit_type: str, outfit_details: str):
        """穿搭模拟"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在模拟穿搭: {outfit_type}")
        print(f"穿搭详情: {outfit_details}")
        
        try:
            result = self.image_editor.outfit_simulation(
                image=image_path,
                outfit_type=outfit_type,
                outfit_details=outfit_details
            )
            
            if result:
                print(f"✅ 穿搭模拟成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 保存至: {result['output_path']}")
            
            return result
        except Exception as e:
            print(f"❌ 穿搭模拟失败: {str(e)}")
            return None
    
    def design_text_poster(self, image_path: str, design_type: str, content: str, style: str = ""):
        """文字设计和海报编辑"""
        if not IMAGE_GENERATION_AVAILABLE or not self.image_editor:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ 图像文件不存在: {image_path}")
            return None
        
        print(f"正在设计{design_type}: {content}")
        if style:
            print(f"设计风格: {style}")
        
        try:
            if design_type in ["文字设计", "艺术字体", "标题设计", "logo设计"]:
                result = self.image_editor.text_design(
                    image=image_path,
                    text_type=design_type,
                    text_content=content,
                    font_style=style or "modern"
                )
            else:
                result = self.image_editor.poster_design(
                    image=image_path,
                    poster_type=design_type,
                    theme=style or content
                )
            
            if result:
                print(f"✅ {design_type}设计成功!")
                print(f"🖼️ 原图: {image_path}")
                print(f"📁 保存至: {result['output_path']}")
            
            return result
        except Exception as e:
            print(f"❌ {design_type}设计失败: {str(e)}")
            return None
    
    def interactive_mode(self):
        print("🤖 欢迎使用AI内容创作系统!")
        print("支持的功能:")
        print("1. 文章写作")
        print("2. 小说创作") 
        print("3. 语音识别")
        if VIDEO_GENERATION_AVAILABLE:
            print("4. 视频生成")
        else:
            print("4. 视频生成 (不可用 - 需要安装额外依赖)")
        print("5. 提示词优化")
        if IMAGE_GENERATION_AVAILABLE:
            print("6. 文本生成图片")
            print("7. 图像编辑")
            print("8. 图片转视频")
        else:
            print("6. 文本生成图片 (不可用 - 需要安装额外依赖)")
            print("7. 图像编辑 (不可用 - 需要安装额外依赖)")
            print("8. 图片转视频 (不可用 - 需要安装额外依赖)")
        print("0. 退出")
        print("-" * 50)
        
        while True:
            try:
                choice = input("\n请选择功能 (0-8): ").strip()
                
                if choice == "0":
                    print("👋 感谢使用AI内容创作系统!")
                    break
                elif choice == "1":
                    self._interactive_article()
                elif choice == "2":
                    self._interactive_novel()
                elif choice == "3":
                    self._interactive_audio()
                elif choice == "4":
                    self._interactive_video()
                elif choice == "5":
                    self._interactive_prompt()
                elif choice == "6":
                    self._interactive_image_generation()
                elif choice == "7":
                    self._interactive_image_editing()
                elif choice == "8":
                    self._interactive_image_to_video()
                else:
                    print("❌ 无效选择，请输入0-8之间的数字")
            
            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
    
    def _interactive_article(self):
        topic = input("请输入文章主题: ").strip()
        if not topic:
            print("❌ 主题不能为空")
            return
        
        print("文章风格选项: informative, narrative, persuasive, technical, casual")
        style = input("请选择文章风格 (默认: informative): ").strip() or "informative"
        
        print("文章长度选项: short, medium, long")
        length = input("请选择文章长度 (默认: medium): ").strip() or "medium"
        
        self.generate_article(topic, style, length)
    
    def _interactive_novel(self):
        print("小说创作选项:")
        print("1. 生成章节")
        print("2. 生成大纲")
        
        choice = input("请选择 (1-2): ").strip()
        
        if choice == "1":
            plot = input("请输入章节剧情: ").strip()
            if not plot:
                print("❌ 剧情不能为空")
                return
            
            characters = input("请输入主要人物 (可选): ").strip()
            setting = input("请输入背景设定 (可选): ").strip()
            
            try:
                chapter_num = int(input("请输入章节编号 (默认: 1): ").strip() or "1")
            except ValueError:
                chapter_num = 1
            
            self.generate_novel_chapter(plot, characters, setting, chapter_num)
        
        elif choice == "2":
            theme = input("请输入小说主题: ").strip()
            if not theme:
                print("❌ 主题不能为空")
                return
            
            genre = input("请输入小说类型 (默认: 现代): ").strip() or "现代"
            length = input("请输入小说长度 (默认: 中篇): ").strip() or "中篇"
            
            self.generate_story_outline(theme, genre, length)
    
    def _interactive_audio(self):
        audio_path = input("请输入音频文件路径: ").strip()
        if not audio_path:
            print("❌ 文件路径不能为空")
            return
        
        print("语言选项: zh (中文), en (英文)")
        language = input("请选择语言 (默认: zh): ").strip() or "zh"
        
        print("摘要类型: 简要, 详细, 要点, 会议纪要")
        summary_type = input("请选择摘要类型 (默认: 详细): ").strip() or "详细"
        
        self.process_audio(audio_path, language, summary_type)
    
    def _interactive_video(self):
        text_prompt = input("请输入视频内容描述: ").strip()
        if not text_prompt:
            print("❌ 内容描述不能为空")
            return
        
        print("视频风格: 教育, 营销, 故事, 解说, 社交")
        video_style = input("请选择视频风格 (默认: 教育): ").strip() or "教育"
        
        try:
            duration = int(input("请输入视频时长/秒 (默认: 30): ").strip() or "30")
        except ValueError:
            duration = 30
        
        print("输出类型: text_video (文字视频), slideshow (幻灯片)")
        output_type = input("请选择输出类型 (默认: text_video): ").strip() or "text_video"
        
        self.generate_video(text_prompt, video_style, duration, output_type)
    
    def _interactive_prompt(self):
        original_prompt = input("请输入需要优化的提示词: ").strip()
        if not original_prompt:
            print("❌ 提示词不能为空")
            return
        
        print("优化目标: 全面优化, 提高清晰度, 增强具体性, 改进结构, 提升可操作性")
        goal = input("请选择优化目标 (默认: 全面优化): ").strip() or "全面优化"
        
        print("应用领域: 通用, 写作, 分析, 创意, 技术, 教育, 营销")
        domain = input("请选择应用领域 (默认: 通用): ").strip() or "通用"
        
        result = self.optimize_prompt(original_prompt, goal, domain)
        
        if result:
            print("\n" + "="*50)
            print("📊 分析结果:")
            print(result['analysis'].get('analysis', '分析信息不可用'))
            print("\n" + "="*50)
            print("✨ 优化结果:")
            print(result['optimization'].get('result', '优化信息不可用'))
    
    def _interactive_image_generation(self):
        if not IMAGE_GENERATION_AVAILABLE:
            print("❌ 图像生成功能不可用")
            print("💡 请安装图像生成依赖: pip install -r requirements-image.txt")
            return
        
        prompt = input("请输入图片描述: ").strip()
        if not prompt:
            print("❌ 图片描述不能为空")
            return
        
        print("艺术风格: 写实, 动漫, 油画, 水彩, 素描, 卡通, 科幻, 梦幻")
        style = input("请选择艺术风格 (默认: 写实): ").strip() or "写实"
        
        try:
            width = int(input("请输入图片宽度 (默认: 512): ").strip() or "512")
            height = int(input("请输入图片高度 (默认: 512): ").strip() or "512")
            num_images = int(input("请输入生成数量 (默认: 1): ").strip() or "1")
        except ValueError:
            width, height, num_images = 512, 512, 1
        
        self.generate_image(prompt, style, width, height, num_images)
    
    def _interactive_image_to_video(self):
        if not (IMAGE_GENERATION_AVAILABLE and VIDEO_GENERATION_AVAILABLE):
            print("❌ 图片转视频功能不可用")
            print("💡 请安装依赖: pip install -r requirements-image.txt requirements-video.txt")
            return
        
        print("图片转视频功能:")
        print("请输入图片文件路径，每行一个，输入空行结束:")
        
        image_paths = []
        while True:
            path = input("图片路径: ").strip()
            if not path:
                break
            if os.path.exists(path):
                image_paths.append(path)
                print(f"✅ 添加图片: {os.path.basename(path)}")
            else:
                print(f"❌ 文件不存在: {path}")
        
        if not image_paths:
            print("❌ 没有有效的图片文件")
            return
        
        try:
            duration = float(input("每张图片显示时长/秒 (默认: 3.0): ").strip() or "3.0")
        except ValueError:
            duration = 3.0
        
        self.create_slideshow_video(image_paths, duration)
    
    def _interactive_image_editing(self):
        if not IMAGE_GENERATION_AVAILABLE:
            print("❌ 图像编辑功能不可用")
            print("💡 请安装图像编辑依赖: pip install -r requirements-image.txt")
            return
        
        image_path = input("请输入图片路径: ").strip()
        if not image_path:
            print("❌ 图片路径不能为空")
            return
        
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return
        
        print("\n编辑模式:")
        print("1. 自由编辑")
        print("2. 视角转换")
        print("3. 风格变换")
        print("4. 环境变换")
        print("5. 对象变换")
        
        mode = input("请选择编辑模式 (1-5): ").strip()
        
        if mode == "1":
            edit_prompt = input("请输入编辑指令: ").strip()
            if edit_prompt:
                self.edit_image(image_path, edit_prompt)
            else:
                print("❌ 编辑指令不能为空")
        
        elif mode == "2":
            print("视角选项: 从正面看, 从侧面看, 从背面看, 从上往下看, 从下往上看, 俯视图, 仰视图")
            view = input("请选择目标视角: ").strip()
            if view:
                try:
                    result = self.image_editor.perspective_transform(image_path, view)
                    if result:
                        print(f"✅ 视角转换成功! 保存至: {result['output_path']}")
                except Exception as e:
                    print(f"❌ 视角转换失败: {e}")
            else:
                print("❌ 目标视角不能为空")
        
        elif mode == "3":
            print("风格选项: 油画风格, 水彩风格, 素描风格, 动漫风格, 照片风格, 印象派, 抽象艺术")
            style = input("请选择目标风格: ").strip()
            if style:
                try:
                    result = self.image_editor.style_transform(image_path, style)
                    if result:
                        print(f"✅ 风格变换成功! 保存至: {result['output_path']}")
                except Exception as e:
                    print(f"❌ 风格变换失败: {e}")
            else:
                print("❌ 目标风格不能为空")
        
        elif mode == "4":
            print("环境选项: 白天转夜晚, 夜晚转白天, 晴天转雨天, 室内转室外, 现代转古代, 城市转乡村, 春天转秋天")
            env = input("请选择环境变换: ").strip()
            if env:
                try:
                    result = self.image_editor.environment_transform(image_path, env)
                    if result:
                        print(f"✅ 环境变换成功! 保存至: {result['output_path']}")
                except Exception as e:
                    print(f"❌ 环境变换失败: {e}")
            else:
                print("❌ 环境变换不能为空")
        
        elif mode == "5":
            print("变换类型: 改变颜色, 改变材质, 改变大小, 添加装饰, 改变表情, 改变姿态, 改变服装")
            transform_type = input("请选择变换类型: ").strip()
            transform_value = input("请输入变换目标值: ").strip()
            if transform_type and transform_value:
                try:
                    result = self.image_editor.object_transform(image_path, transform_type, transform_value)
                    if result:
                        print(f"✅ 对象变换成功! 保存至: {result['output_path']}")
                except Exception as e:
                    print(f"❌ 对象变换失败: {e}")
            else:
                print("❌ 变换类型和目标值都不能为空")
        
        else:
            print("❌ 无效选择")

def main():
    parser = argparse.ArgumentParser(description="AI内容创作系统")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--article", help="生成文章，指定主题")
    parser.add_argument("--audio", help="处理音频文件，指定文件路径")
    parser.add_argument("--video", help="生成视频，指定内容描述")
    parser.add_argument("--optimize-prompt", help="优化提示词")
    parser.add_argument("--generate-image", help="生成图片，指定描述")
    parser.add_argument("--edit-image", help="编辑图片，格式：图片路径,编辑指令")
    parser.add_argument("--image-to-video", help="图片转视频，指定图片目录")
    parser.add_argument("--generate-avatar", help="生成虚拟形象，格式：形象类型,描述")
    parser.add_argument("--ai-remove", help="AI消除，格式：图片路径,消除类型,目标对象")
    parser.add_argument("--ai-redraw", help="AI重绘，格式：图片路径,重绘类型,描述")
    parser.add_argument("--virtual-scene", help="虚拟场景，格式：图片路径,场景类型,场景元素")
    parser.add_argument("--outfit-sim", help="穿搭模拟，格式：图片路径,穿搭类型,穿搭详情")
    parser.add_argument("--text-poster", help="文字海报，格式：图片路径,设计类型,内容,风格")
    
    args = parser.parse_args()
    
    system = AI2CSystem()
    
    if args.interactive or len(sys.argv) == 1:
        system.interactive_mode()
    elif args.article:
        system.generate_article(args.article)
    elif args.audio:
        system.process_audio(args.audio)
    elif args.video:
        system.generate_video(args.video)
    elif args.optimize_prompt:
        system.optimize_prompt(args.optimize_prompt)
    elif args.generate_image:
        system.generate_image(args.generate_image)
    elif args.edit_image:
        if "," in args.edit_image:
            image_path, edit_prompt = args.edit_image.split(",", 1)
            system.edit_image(image_path.strip(), edit_prompt.strip())
        else:
            print("❌ 请使用格式: --edit-image '图片路径,编辑指令'")
    elif args.image_to_video:
        import glob
        image_paths = glob.glob(os.path.join(args.image_to_video, "*.{jpg,jpeg,png,webp}"))
        if image_paths:
            system.create_slideshow_video(image_paths)
        else:
            print(f"❌ 在目录 {args.image_to_video} 中没有找到图片文件")
    elif args.generate_avatar:
        if "," in args.generate_avatar:
            avatar_type, description = args.generate_avatar.split(",", 1)
            system.generate_avatar(avatar_type.strip(), description.strip())
        else:
            system.generate_avatar(args.generate_avatar.strip())
    elif args.ai_remove:
        parts = args.ai_remove.split(",")
        if len(parts) >= 2:
            image_path = parts[0].strip()
            remove_type = parts[1].strip()
            target_object = parts[2].strip() if len(parts) > 2 else ""
            system.ai_remove_object(image_path, remove_type, target_object)
        else:
            print("❌ 请使用格式: --ai-remove '图片路径,消除类型,目标对象'")
    elif args.ai_redraw:
        parts = args.ai_redraw.split(",")
        if len(parts) >= 3:
            image_path = parts[0].strip()
            redraw_type = parts[1].strip()
            description = parts[2].strip()
            system.ai_redraw_area(image_path, redraw_type, description)
        else:
            print("❌ 请使用格式: --ai-redraw '图片路径,重绘类型,描述'")
    elif args.virtual_scene:
        parts = args.virtual_scene.split(",")
        if len(parts) >= 2:
            image_path = parts[0].strip()
            scene_type = parts[1].strip()
            scene_elements = parts[2].strip() if len(parts) > 2 else ""
            system.create_virtual_scene(image_path, scene_type, scene_elements)
        else:
            print("❌ 请使用格式: --virtual-scene '图片路径,场景类型,场景元素'")
    elif args.outfit_sim:
        parts = args.outfit_sim.split(",")
        if len(parts) >= 3:
            image_path = parts[0].strip()
            outfit_type = parts[1].strip()
            outfit_details = parts[2].strip()
            system.simulate_outfit(image_path, outfit_type, outfit_details)
        else:
            print("❌ 请使用格式: --outfit-sim '图片路径,穿搭类型,穿搭详情'")
    elif args.text_poster:
        parts = args.text_poster.split(",")
        if len(parts) >= 3:
            image_path = parts[0].strip()
            design_type = parts[1].strip()
            content = parts[2].strip()
            style = parts[3].strip() if len(parts) > 3 else ""
            system.design_text_poster(image_path, design_type, content, style)
        else:
            print("❌ 请使用格式: --text-poster '图片路径,设计类型,内容,风格'")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()