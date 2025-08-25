import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from ..content_generation.llm_client import LLMClient

# 可选依赖检查
try:
    from moviepy.editor import (
        VideoFileClip, ImageClip, TextClip, CompositeVideoClip, 
        AudioFileClip, concatenate_videoclips
    )
    import cv2
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ 视频生成依赖未安装，运行以下命令安装:")
    print("pip install -r requirements-video.txt")

class VideoGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.output_dir = "./outputs/videos"
        self.temp_dir = "./temp"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.moviepy_available = MOVIEPY_AVAILABLE
    
    def _check_video_dependencies(self):
        if not self.moviepy_available:
            raise ImportError(
                "视频生成功能需要额外依赖，请运行: pip install -r requirements-video.txt"
            )
    
    def generate_video_script(self, text_prompt: str, video_style: str = "教育", duration: int = 30) -> Dict[str, Any]:
        style_prompts = {
            "教育": "教育性和信息性的视频，适合学习和教学",
            "营销": "吸引人的营销视频，突出产品或服务的优势",
            "故事": "叙述性视频，有完整的故事情节",
            "解说": "解说类视频，适合讲解和演示",
            "社交": "适合社交媒体的短视频，轻松有趣"
        }
        
        prompt = f"""
根据以下要求，为一个{duration}秒的视频创建详细的脚本：

内容主题：{text_prompt}
视频风格：{style_prompts.get(video_style, video_style)}
时长：{duration}秒

请提供以下内容：
1. 视频标题（吸引人的标题）
2. 开头介绍（3-5秒）
3. 主要内容分段（每段5-10秒，包含画面描述和解说词）
4. 结尾总结（3-5秒）
5. 关键画面描述（每个场景的视觉元素）
6. 配音文本（完整的解说词）
7. 建议的背景音乐类型
8. 转场效果建议

请以JSON格式返回，包含以下字段：
- title: 视频标题
- duration: 总时长
- scenes: 场景列表，每个场景包含 start_time, end_time, visual_description, narration, transition
- full_narration: 完整配音文本
- music_style: 建议的音乐风格
- visual_style: 视觉风格描述

格式示例：
{{
    "title": "视频标题",
    "duration": {duration},
    "scenes": [
        {{
            "start_time": 0,
            "end_time": 5,
            "visual_description": "开场画面描述",
            "narration": "开场解说词",
            "transition": "淡入"
        }}
    ],
    "full_narration": "完整的配音文本",
    "music_style": "轻松愉快",
    "visual_style": "现代简洁"
}}
"""
        
        script_text = self.llm_client.generate(prompt, max_tokens=3000, temperature=0.7)
        
        try:
            script_data = json.loads(script_text)
        except json.JSONDecodeError:
            script_data = {
                "title": f"{text_prompt} - 视频",
                "duration": duration,
                "scenes": [
                    {
                        "start_time": 0,
                        "end_time": duration,
                        "visual_description": "根据文本内容生成的视觉画面",
                        "narration": script_text[:500] + "..." if len(script_text) > 500 else script_text,
                        "transition": "淡入淡出"
                    }
                ],
                "full_narration": script_text,
                "music_style": "背景音乐",
                "visual_style": "简洁现代"
            }
        
        return script_data
    
    def create_text_video(
        self, 
        script: Dict[str, Any], 
        background_color: tuple = (255, 255, 255),
        text_color: tuple = (0, 0, 0),
        font_size: int = 40,
        resolution: tuple = (1920, 1080)
    ) -> str:
        self._check_video_dependencies()
        
        clips = []
        
        for scene in script['scenes']:
            duration = scene['end_time'] - scene['start_time']
            
            text_clip = TextClip(
                scene['narration'],
                fontsize=font_size,
                color='white' if sum(background_color) < 400 else 'black',
                font='Arial-Bold',
                size=resolution
            ).set_duration(duration).set_start(scene['start_time'])
            
            background_clip = self._create_background_clip(
                duration, 
                background_color, 
                resolution
            ).set_start(scene['start_time'])
            
            scene_clip = CompositeVideoClip([background_clip, text_clip])
            clips.append(scene_clip)
        
        final_video = concatenate_videoclips(clips, method="compose")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"{timestamp}_{script['title'][:20]}.mp4")
        
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac'
        )
        
        return output_path
    
    def create_slideshow_video(
        self, 
        script: Dict[str, Any],
        image_paths: List[str] = None,
        transition_duration: float = 0.5
    ) -> str:
        self._check_video_dependencies()
        
        clips = []
        
        if not image_paths:
            image_paths = self._generate_placeholder_images(len(script['scenes']))
        
        for i, scene in enumerate(script['scenes']):
            duration = scene['end_time'] - scene['start_time']
            
            if i < len(image_paths):
                image_clip = ImageClip(image_paths[i], duration=duration)
                
                text_clip = TextClip(
                    scene['narration'],
                    fontsize=30,
                    color='white',
                    font='Arial-Bold',
                    size=(1600, 200)
                ).set_position(('center', 'bottom')).set_duration(duration)
                
                scene_clip = CompositeVideoClip([image_clip, text_clip])
            else:
                scene_clip = self._create_text_scene(scene, duration)
            
            if i > 0:
                scene_clip = scene_clip.crossfadein(transition_duration)
            
            clips.append(scene_clip)
        
        final_video = concatenate_videoclips(clips, method="compose")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"{timestamp}_slideshow_{script['title'][:20]}.mp4")
        
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264'
        )
        
        return output_path
    
    def add_background_music(self, video_path: str, music_path: str, volume: float = 0.3) -> str:
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(music_path)
            
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            else:
                audio = audio.loop(duration=video.duration)
            
            audio = audio.volumex(volume)
            
            final_video = video.set_audio(audio)
            
            output_path = video_path.replace('.mp4', '_with_music.mp4')
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac'
            )
            
            return output_path
        
        except Exception as e:
            print(f"添加背景音乐失败: {str(e)}")
            return video_path
    
    def _create_background_clip(self, duration: float, color: tuple, resolution: tuple):
        color_array = np.full((resolution[1], resolution[0], 3), color, dtype=np.uint8)
        return ImageClip(color_array, duration=duration)
    
    def _create_text_scene(self, scene: Dict[str, Any], duration: float):
        text_clip = TextClip(
            scene['narration'],
            fontsize=40,
            color='white',
            font='Arial-Bold',
            size=(1920, 1080)
        ).set_duration(duration)
        
        background_clip = self._create_background_clip(
            duration, 
            (50, 50, 50), 
            (1920, 1080)
        )
        
        return CompositeVideoClip([background_clip, text_clip])
    
    def _generate_placeholder_images(self, count: int) -> List[str]:
        image_paths = []
        
        for i in range(count):
            img = Image.new('RGB', (1920, 1080), color=(100 + i * 30, 150 + i * 20, 200 + i * 10))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            text = f"场景 {i + 1}"
            draw.text((960, 540), text, fill=(255, 255, 255), font=font, anchor="mm")
            
            image_path = os.path.join(self.temp_dir, f"placeholder_{i}.png")
            img.save(image_path)
            image_paths.append(image_path)
        
        return image_paths
    
    def generate_video_from_text(
        self, 
        text_prompt: str, 
        video_style: str = "教育",
        duration: int = 30,
        output_type: str = "text_video"
    ) -> Dict[str, Any]:
        
        print("生成视频脚本...")
        script = self.generate_video_script(text_prompt, video_style, duration)
        
        print("创建视频...")
        if output_type == "slideshow":
            video_path = self.create_slideshow_video(script)
        else:
            video_path = self.create_text_video(script)
        
        result = {
            "script": script,
            "video_path": video_path,
            "metadata": {
                "text_prompt": text_prompt,
                "video_style": video_style,
                "duration": duration,
                "output_type": output_type,
                "created_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(video_path) if os.path.exists(video_path) else 0
            }
        }
        
        return result
    
    def cleanup_temp_files(self):
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")