import os
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import json

# 可选依赖检查
try:
    from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.fx import resize, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ 视频生成依赖未安装，运行以下命令安装:")
    print("pip install -r requirements-video.txt")

class ImageToVideoGenerator:
    def __init__(self):
        self.output_dir = "./outputs/videos"
        self.temp_dir = "./temp"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.moviepy_available = MOVIEPY_AVAILABLE
        
        # 预定义的视频效果
        self.effects = {
            "静态": "static",
            "淡入淡出": "fade",
            "放大缩小": "zoom",
            "平移": "pan",
            "旋转": "rotate",
            "幻灯片": "slideshow"
        }
        
        # 转场效果
        self.transitions = {
            "切换": "cut",
            "淡化": "fade",
            "滑动": "slide",
            "推拉": "push"
        }
    
    def _check_dependencies(self):
        """检查视频生成依赖"""
        if not self.moviepy_available:
            raise ImportError(
                "图片转视频功能需要额外依赖，请运行: pip install -r requirements-video.txt"
            )
    
    def load_images(self, image_paths: List[str]) -> List[Image.Image]:
        """加载图像文件"""
        images = []
        
        for path in image_paths:
            try:
                if isinstance(path, str) and os.path.exists(path):
                    image = Image.open(path)
                    images.append(image)
                    print(f"✅ 加载图像: {os.path.basename(path)}")
                elif hasattr(path, 'save'):  # PIL Image对象
                    images.append(path)
                    print(f"✅ 加载PIL图像对象")
                else:
                    print(f"❌ 无法加载图像: {path}")
            except Exception as e:
                print(f"❌ 加载图像失败 {path}: {e}")
        
        return images
    
    def create_slideshow_video(
        self,
        image_paths: List[Union[str, Image.Image]],
        duration_per_image: float = 3.0,
        transition_duration: float = 0.5,
        output_size: tuple = (1920, 1080),
        fps: int = 24,
        background_music: str = None
    ) -> Dict[str, Any]:
        """创建幻灯片视频"""
        self._check_dependencies()
        
        print(f"🎬 开始创建幻灯片视频...")
        print(f"📸 图片数量: {len(image_paths)}")
        print(f"⏱️ 每张图片时长: {duration_per_image}秒")
        
        # 加载图像
        images = []
        for item in image_paths:
            if isinstance(item, str):
                if os.path.exists(item):
                    images.append(item)
                else:
                    print(f"⚠️ 图片文件不存在: {item}")
            elif hasattr(item, 'save'):  # PIL Image
                # 保存PIL图像到临时文件
                temp_path = os.path.join(self.temp_dir, f"temp_img_{len(images)}.png")
                item.save(temp_path)
                images.append(temp_path)
        
        if not images:
            raise ValueError("没有有效的图像文件")
        
        try:
            clips = []
            
            for i, image_path in enumerate(images):
                print(f"🔄 处理图像 {i+1}/{len(images)}")
                
                # 创建图像剪辑
                clip = ImageClip(image_path, duration=duration_per_image)
                
                # 调整大小
                clip = clip.resize(output_size)
                
                # 添加淡入淡出效果
                if transition_duration > 0:
                    if i > 0:  # 不是第一张图片
                        clip = clip.fadein(transition_duration)
                    if i < len(images) - 1:  # 不是最后一张图片
                        clip = clip.fadeout(transition_duration)
                
                clips.append(clip)
            
            # 合并所有剪辑
            final_video = concatenate_videoclips(clips, method="compose")
            
            # 添加背景音乐
            if background_music and os.path.exists(background_music):
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(background_music)
                
                if audio.duration > final_video.duration:
                    audio = audio.subclip(0, final_video.duration)
                else:
                    audio = audio.loop(duration=final_video.duration)
                
                final_video = final_video.set_audio(audio.volumex(0.3))
            
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"slideshow_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # 输出视频
            print(f"💾 正在保存视频到: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac' if background_music else None
            )
            
            # 清理资源
            final_video.close()
            for clip in clips:
                clip.close()
            
            result = {
                "video_path": output_path,
                "metadata": {
                    "image_count": len(images),
                    "duration_per_image": duration_per_image,
                    "transition_duration": transition_duration,
                    "total_duration": len(images) * duration_per_image,
                    "output_size": output_size,
                    "fps": fps,
                    "background_music": background_music,
                    "created_at": datetime.now().isoformat(),
                    "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
            }
            
            print(f"✅ 幻灯片视频创建完成!")
            return result
            
        except Exception as e:
            print(f"❌ 视频创建失败: {e}")
            raise e
        
        finally:
            # 清理临时文件
            self._cleanup_temp_images()
    
    def create_animated_video(
        self,
        image_path: Union[str, Image.Image],
        animation_type: str = "zoom",
        duration: float = 5.0,
        output_size: tuple = (1920, 1080),
        fps: int = 30
    ) -> Dict[str, Any]:
        """创建单图片动画视频"""
        self._check_dependencies()
        
        print(f"🎬 创建动画视频，效果: {animation_type}")
        
        # 处理输入图像
        if isinstance(image_path, str):
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            temp_image_path = image_path
        else:  # PIL Image
            temp_image_path = os.path.join(self.temp_dir, "temp_animation.png")
            image_path.save(temp_image_path)
        
        try:
            clip = ImageClip(temp_image_path, duration=duration)
            clip = clip.resize(output_size)
            
            # 根据动画类型应用效果
            if animation_type == "zoom":
                # 缩放效果
                def zoom_effect(get_frame, t):
                    frame = get_frame(t)
                    zoom_factor = 1 + (t / duration) * 0.3  # 逐渐放大30%
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
                    
                    # 调整大小
                    resized = cv2.resize(frame, (new_w, new_h))
                    
                    # 居中裁剪
                    start_x = (new_w - w) // 2
                    start_y = (new_h - h) // 2
                    result = resized[start_y:start_y + h, start_x:start_x + w]
                    
                    return result
                
                clip = clip.fl(zoom_effect)
            
            elif animation_type == "pan":
                # 平移效果
                def pan_effect(get_frame, t):
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    
                    # 创建稍大的canvas
                    canvas_w, canvas_h = int(w * 1.2), int(h * 1.2)
                    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
                    
                    # 计算位置
                    progress = t / duration
                    start_x = int((canvas_w - w) * progress)
                    start_y = int((canvas_h - h) * 0.1)
                    
                    # 放置图像
                    canvas[start_y:start_y + h, start_x:start_x + w] = frame
                    
                    # 裁剪回原始大小
                    crop_x = (canvas_w - w) // 2
                    crop_y = (canvas_h - h) // 2
                    result = canvas[crop_y:crop_y + h, crop_x:crop_x + w]
                    
                    return result
                
                clip = clip.fl(pan_effect)
            
            elif animation_type == "fade":
                # 淡入淡出效果
                fade_duration = min(1.0, duration / 3)
                clip = clip.fadein(fade_duration).fadeout(fade_duration)
            
            # 生成输出文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"animated_{animation_type}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            print(f"💾 正在保存动画视频...")
            clip.write_videofile(
                output_path,
                fps=fps,
                codec='libx264'
            )
            
            clip.close()
            
            result = {
                "video_path": output_path,
                "metadata": {
                    "animation_type": animation_type,
                    "duration": duration,
                    "output_size": output_size,
                    "fps": fps,
                    "created_at": datetime.now().isoformat(),
                    "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
            }
            
            print(f"✅ 动画视频创建完成!")
            return result
            
        except Exception as e:
            print(f"❌ 动画视频创建失败: {e}")
            raise e
        
        finally:
            # 清理临时文件
            if temp_image_path != image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    
    def create_comparison_video(
        self,
        before_image: Union[str, Image.Image],
        after_image: Union[str, Image.Image],
        comparison_type: str = "side_by_side",
        duration: float = 10.0,
        transition_point: float = 5.0,
        output_size: tuple = (1920, 1080)
    ) -> Dict[str, Any]:
        """创建对比视频"""
        self._check_dependencies()
        
        print(f"🎬 创建对比视频，类型: {comparison_type}")
        
        # 处理输入图像
        temp_paths = []
        for i, image in enumerate([before_image, after_image]):
            if isinstance(image, str):
                temp_paths.append(image)
            else:
                temp_path = os.path.join(self.temp_dir, f"temp_compare_{i}.png")
                image.save(temp_path)
                temp_paths.append(temp_path)
        
        try:
            clip1 = ImageClip(temp_paths[0], duration=duration).resize(output_size)
            clip2 = ImageClip(temp_paths[1], duration=duration).resize(output_size)
            
            if comparison_type == "side_by_side":
                # 并排对比
                # 调整每个图像为一半宽度
                half_width = output_size[0] // 2
                clip1 = clip1.resize((half_width, output_size[1])).set_position(('left'))
                clip2 = clip2.resize((half_width, output_size[1])).set_position(('right'))
                
                final_clip = CompositeVideoClip([clip1, clip2])
                
            elif comparison_type == "transition":
                # 转场对比
                clip1 = clip1.set_duration(transition_point).fadeout(0.5)
                clip2 = clip2.set_start(transition_point).fadein(0.5)
                
                final_clip = CompositeVideoClip([clip1, clip2])
                
            else:  # before_after
                # 前后对比
                final_clip = concatenate_videoclips([clip1.set_duration(duration/2), 
                                                   clip2.set_duration(duration/2)])
            
            # 生成输出文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"comparison_{comparison_type}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            print(f"💾 正在保存对比视频...")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264'
            )
            
            # 清理资源
            final_clip.close()
            clip1.close()
            clip2.close()
            
            result = {
                "video_path": output_path,
                "metadata": {
                    "comparison_type": comparison_type,
                    "duration": duration,
                    "transition_point": transition_point if comparison_type == "transition" else None,
                    "output_size": output_size,
                    "created_at": datetime.now().isoformat(),
                    "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
            }
            
            print(f"✅ 对比视频创建完成!")
            return result
            
        except Exception as e:
            print(f"❌ 对比视频创建失败: {e}")
            raise e
        
        finally:
            # 清理临时文件
            for temp_path in temp_paths:
                if temp_path != before_image and temp_path != after_image and os.path.exists(temp_path):
                    os.remove(temp_path)
    
    def batch_create_videos(
        self,
        image_groups: List[List[str]],
        video_type: str = "slideshow",
        **kwargs
    ) -> Dict[str, Any]:
        """批量创建视频"""
        results = []
        failed_groups = []
        
        for i, image_group in enumerate(image_groups):
            print(f"\n🔄 处理第 {i+1}/{len(image_groups)} 组图片")
            
            try:
                if video_type == "slideshow":
                    result = self.create_slideshow_video(image_group, **kwargs)
                else:
                    # 对于单图动画，只取第一张图片
                    result = self.create_animated_video(image_group[0], **kwargs)
                
                results.append({
                    "group_index": i,
                    "image_group": image_group,
                    "result": result
                })
                
            except Exception as e:
                print(f"❌ 第 {i+1} 组处理失败: {e}")
                failed_groups.append({
                    "group_index": i,
                    "image_group": image_group,
                    "error": str(e)
                })
        
        return {
            "successful_results": results,
            "failed_groups": failed_groups,
            "total_processed": len(image_groups),
            "success_count": len(results),
            "failure_count": len(failed_groups)
        }
    
    def _cleanup_temp_images(self):
        """清理临时图像文件"""
        try:
            for filename in os.listdir(self.temp_dir):
                if filename.startswith("temp_") and filename.endswith((".png", ".jpg", ".jpeg")):
                    filepath = os.path.join(self.temp_dir, filename)
                    os.remove(filepath)
        except Exception as e:
            print(f"清理临时文件时出错: {e}")
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        if not os.path.exists(video_path):
            return None
        
        try:
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "file_size": os.path.getsize(video_path)
            }
            clip.close()
            return info
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None