import os
import json
import torch
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import numpy as np
from ..content_generation.llm_client import LLMClient

# 可选依赖检查
try:
    from diffusers import (
        StableDiffusionPipeline, 
        StableDiffusionXLPipeline,
        DPMSolverMultistepScheduler,
        EulerAncestralDiscreteScheduler
    )
    from transformers import AutoTokenizer
    import accelerate
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("⚠️ 图像生成依赖未安装，运行以下命令安装:")
    print("pip install -r requirements-image.txt")

class TextToImageGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.output_dir = "./outputs/images"
        os.makedirs(self.output_dir, exist_ok=True)
        self.diffusers_available = DIFFUSERS_AVAILABLE
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 默认模型配置
        self.default_models = {
            "sd15": "runwayml/stable-diffusion-v1-5",
            "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
            "sd21": "stabilityai/stable-diffusion-2-1"
        }
        
        # 预定义风格
        self.style_prompts = {
            "写实": "photorealistic, highly detailed, professional photography",
            "动漫": "anime style, manga, cel shading, vibrant colors",
            "油画": "oil painting, classical art style, brush strokes",
            "水彩": "watercolor painting, soft colors, artistic",
            "素描": "pencil sketch, black and white, detailed drawing",
            "卡通": "cartoon style, colorful, simple shapes",
            "科幻": "sci-fi, futuristic, cyberpunk, neon lights",
            "梦幻": "dreamy, surreal, ethereal, magical"
        }
    
    def _check_dependencies(self):
        """检查图像生成依赖"""
        if not self.diffusers_available:
            raise ImportError(
                "图像生成功能需要额外依赖，请运行: pip install -r requirements-image.txt"
            )
    
    def load_pipeline(self, model_name: str = "sd15"):
        """加载图像生成模型"""
        self._check_dependencies()
        
        if self.pipeline is not None:
            return
        
        print(f"🔄 正在加载图像生成模型: {model_name}")
        
        try:
            model_id = self.default_models.get(model_name, model_name)
            
            if model_name == "sdxl":
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    use_safetensors=True,
                    variant="fp16" if self.device == "cuda" else None
                )
            else:
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    use_safetensors=True
                )
            
            # 优化设置
            if self.device == "cuda":
                self.pipeline = self.pipeline.to(self.device)
                self.pipeline.enable_memory_efficient_attention()
                try:
                    self.pipeline.enable_xformers_memory_efficient_attention()
                except:
                    pass
            
            # 设置调度器
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            print(f"✅ 模型加载完成，使用设备: {self.device}")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise e
    
    def optimize_prompt(self, user_prompt: str, language: str = "zh") -> str:
        """使用LLM优化图像生成提示词"""
        if language == "zh":
            optimization_prompt = f"""
请将以下中文描述转换为适合AI图像生成的英文提示词：

用户描述：{user_prompt}

要求：
1. 转换为详细的英文描述
2. 包含具体的视觉元素（颜色、光线、构图等）
3. 添加画质相关词汇（如high quality, detailed, 8k等）
4. 保持原意不变，但让描述更加具体和生动
5. 使用逗号分隔不同的描述元素

请只返回优化后的英文提示词，不需要其他解释：
"""
        else:
            optimization_prompt = f"""
Optimize the following prompt for AI image generation:

User prompt: {user_prompt}

Requirements:
1. Make it more detailed and specific
2. Add visual elements (colors, lighting, composition)
3. Include quality keywords (high quality, detailed, 8k, etc.)
4. Use comma-separated keywords
5. Keep the original meaning

Return only the optimized prompt:
"""
        
        try:
            optimized = self.llm_client.generate(
                optimization_prompt, 
                max_tokens=200,
                temperature=0.7
            )
            return optimized.strip()
        except Exception as e:
            print(f"提示词优化失败，使用原始提示词: {e}")
            return user_prompt
    
    def generate_image(
        self,
        prompt: str,
        style: str = "写实",
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        steps: int = 20,
        guidance_scale: float = 7.5,
        negative_prompt: str = None,
        seed: int = None,
        optimize_prompt: bool = True,
        model_name: str = "sd15"
    ) -> Dict[str, Any]:
        """生成图像"""
        self._check_dependencies()
        
        # 加载模型
        if self.pipeline is None:
            self.load_pipeline(model_name)
        
        # 优化提示词
        if optimize_prompt:
            print("🔄 正在优化提示词...")
            prompt = self.optimize_prompt(prompt)
            print(f"✨ 优化后的提示词: {prompt}")
        
        # 添加风格
        style_addition = self.style_prompts.get(style, "")
        if style_addition:
            prompt = f"{prompt}, {style_addition}"
        
        # 默认负面提示词
        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, deformed, watermark, text"
        
        # 设置随机种子
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        else:
            seed = np.random.randint(0, 2**32 - 1)
            torch.manual_seed(seed)
        
        print(f"🎨 开始生成图像...")
        print(f"📝 提示词: {prompt}")
        print(f"🎭 风格: {style}")
        print(f"📏 尺寸: {width}x{height}")
        print(f"🎯 生成数量: {num_images}")
        
        try:
            # 生成参数
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_images_per_prompt": num_images,
                "num_inference_steps": steps,
                "guidance_scale": guidance_scale,
                "width": width,
                "height": height,
                "generator": torch.Generator(device=self.device).manual_seed(seed)
            }
            
            # 生成图像
            result = self.pipeline(**generation_kwargs)
            images = result.images
            
            # 保存图像
            saved_paths = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, image in enumerate(images):
                filename = f"{timestamp}_img_{i+1}_seed_{seed}.png"
                filepath = os.path.join(self.output_dir, filename)
                image.save(filepath)
                saved_paths.append(filepath)
            
            generation_info = {
                "images": images,
                "saved_paths": saved_paths,
                "metadata": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "style": style,
                    "width": width,
                    "height": height,
                    "num_images": num_images,
                    "steps": steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed,
                    "model_name": model_name,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            print(f"✅ 图像生成完成! 保存到: {saved_paths}")
            return generation_info
            
        except Exception as e:
            print(f"❌ 图像生成失败: {e}")
            raise e
    
    def generate_batch_images(
        self,
        prompts: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """批量生成图像"""
        results = []
        failed_prompts = []
        
        for i, prompt in enumerate(prompts):
            print(f"\n🔄 处理第 {i+1}/{len(prompts)} 个提示词")
            try:
                result = self.generate_image(prompt, **kwargs)
                results.append({
                    "prompt": prompt,
                    "result": result
                })
            except Exception as e:
                print(f"❌ 提示词 '{prompt}' 生成失败: {e}")
                failed_prompts.append({
                    "prompt": prompt,
                    "error": str(e)
                })
        
        return {
            "successful_results": results,
            "failed_prompts": failed_prompts,
            "total_processed": len(prompts),
            "success_count": len(results),
            "failure_count": len(failed_prompts)
        }
    
    def create_image_grid(self, images: List[Image.Image], grid_size: Tuple[int, int] = None) -> Image.Image:
        """创建图像网格"""
        if not images:
            return None
        
        # 自动计算网格大小
        if grid_size is None:
            cols = int(np.ceil(np.sqrt(len(images))))
            rows = int(np.ceil(len(images) / cols))
            grid_size = (cols, rows)
        
        cols, rows = grid_size
        
        # 获取单个图像尺寸
        img_width, img_height = images[0].size
        
        # 创建网格画布
        grid_width = cols * img_width
        grid_height = rows * img_height
        grid_image = Image.new('RGB', (grid_width, grid_height), color='white')
        
        # 粘贴图像到网格
        for idx, image in enumerate(images):
            if idx >= cols * rows:
                break
            
            row = idx // cols
            col = idx % cols
            
            x = col * img_width
            y = row * img_height
            
            grid_image.paste(image, (x, y))
        
        return grid_image
    
    def save_generation_info(self, generation_info: Dict[str, Any], filename: str = None) -> str:
        """保存生成信息到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_generation_info.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 准备可序列化的数据
        serializable_info = generation_info.copy()
        serializable_info.pop('images', None)  # 移除PIL图像对象
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_info, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def cleanup_model(self):
        """清理模型释放显存"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("🧹 模型已清理，显存已释放")