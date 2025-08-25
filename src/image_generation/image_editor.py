import os
import torch
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import numpy as np
from ..content_generation.llm_client import LLMClient

# 可选依赖检查
try:
    from diffusers import (
        QwenImageEditPipeline, 
        StableDiffusionInpaintPipeline,
        StableDiffusionXLInpaintPipeline,
        ControlNetModel,
        StableDiffusionControlNetInpaintPipeline
    )
    QWEN_IMAGE_EDIT_AVAILABLE = True
except ImportError:
    QWEN_IMAGE_EDIT_AVAILABLE = False
    print("⚠️ Qwen图像编辑依赖未安装，运行以下命令安装:")
    print("pip install -r requirements-image.txt")

# 其他模型依赖
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from segment_anything import SamPredictor, sam_model_registry
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False

class ImageEditor:
    def __init__(self):
        self.llm_client = LLMClient()
        self.output_dir = "./outputs/images/edited"
        os.makedirs(self.output_dir, exist_ok=True)
        self.qwen_available = QWEN_IMAGE_EDIT_AVAILABLE
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 预定义的编辑模板
        self.editing_templates = {
            "视角转换": {
                "从正面看": "Change the view to front view, clear and detailed",
                "从侧面看": "Change the view to side view, clear and detailed", 
                "从背面看": "Change the view to back view, clear and detailed",
                "从上往下看": "Change the view to top-down view, bird's eye view",
                "从下往上看": "Change the view to bottom-up view, low angle view",
                "俯视图": "Convert to aerial view, overhead perspective",
                "仰视图": "Convert to upward view, worm's eye view"
            },
            "风格转换": {
                "油画风格": "Convert to oil painting style, artistic brush strokes",
                "水彩风格": "Convert to watercolor style, soft and flowing",
                "素描风格": "Convert to pencil sketch style, black and white drawing",
                "动漫风格": "Convert to anime style, manga artwork",
                "照片风格": "Convert to photorealistic style, highly detailed",
                "印象派": "Convert to impressionist painting style",
                "抽象艺术": "Convert to abstract art style"
            },
            "环境变换": {
                "白天转夜晚": "Change from day to night, add moonlight and stars",
                "夜晚转白天": "Change from night to day, add bright sunlight",
                "晴天转雨天": "Change to rainy weather, add rain drops and clouds",
                "室内转室外": "Move the scene from indoor to outdoor setting",
                "现代转古代": "Change the setting from modern to ancient times",
                "城市转乡村": "Change the setting from city to countryside",
                "春天转秋天": "Change the season from spring to autumn"
            },
            "对象变换": {
                "改变颜色": "Change the color to {color}",
                "改变材质": "Change the material to {material}",
                "改变大小": "Change the size to {size}",
                "添加装饰": "Add decorative elements like {decoration}",
                "改变表情": "Change the facial expression to {expression}",
                "改变姿态": "Change the pose to {pose}",
                "改变服装": "Change the clothing to {clothing}"
            },
            "虚拟形象生成": {
                "生成3D虚拟人": "Generate a 3D virtual avatar, realistic human appearance",
                "卡通角色": "Create cartoon character avatar, stylized and cute",
                "动漫人物": "Generate anime character, manga style illustration",
                "游戏角色": "Create game character design, fantasy RPG style",
                "商务形象": "Generate professional business avatar, formal appearance",
                "时尚模特": "Create fashion model avatar, trendy and stylish"
            },
            "AI消除": {
                "移除对象": "Remove the {object} from the image completely",
                "消除水印": "Remove watermarks and logos from the image",
                "清除背景": "Remove background, make it transparent or solid color",
                "去除文字": "Remove all text and writing from the image",
                "消除瑕疵": "Remove imperfections, spots, and blemishes",
                "删除人物": "Remove people from the image"
            },
            "AI重绘": {
                "局部重绘": "Redraw the selected area with {description}",
                "背景重绘": "Redraw the background as {background}",
                "人物重绘": "Redraw the person with {features}",
                "物体重绘": "Redraw the object as {new_object}",
                "全图重绘": "Completely redraw the image in {style} style",
                "细节重绘": "Enhance and redraw fine details"
            },
            "虚拟场景": {
                "科幻场景": "Transform into futuristic sci-fi environment",
                "奇幻世界": "Create fantasy world with magical elements",
                "历史场景": "Transform into historical setting of {period}",
                "自然风光": "Create natural landscape scene with {elements}",
                "城市场景": "Generate urban cityscape environment",
                "室内空间": "Create interior space design for {room_type}"
            },
            "穿搭模拟": {
                "换装试衣": "Change clothing to {clothing_style}",
                "配饰搭配": "Add accessories like {accessories}",
                "发型变换": "Change hairstyle to {hairstyle}",
                "妆容调整": "Adjust makeup style to {makeup_style}",
                "颜色搭配": "Change color scheme to {color_theme}",
                "季节穿搭": "Change outfit for {season} season"
            },
            "文字设计": {
                "艺术字体": "Add artistic text '{text}' with {font_style} style",
                "标题设计": "Design title text '{title}' with professional layout",
                "logo设计": "Create logo design with text '{logo_text}'",
                "书法字体": "Add calligraphy text '{text}' in {calligraphy_style}",
                "立体文字": "Create 3D text effect for '{text}'",
                "霓虹文字": "Add neon light text effect for '{text}'"
            },
            "海报编辑": {
                "电影海报": "Design movie poster style with {theme}",
                "音乐海报": "Create music concert poster design",
                "活动海报": "Design event poster for {event_type}",
                "产品海报": "Create product advertisement poster",
                "复古海报": "Design vintage poster style with retro elements",
                "简约海报": "Create minimalist poster design"
            }
        }
        
        # 模型管道存储
        self.pipelines = {
            'qwen_edit': None,
            'inpaint': None,
            'inpaint_xl': None,
            'controlnet_inpaint': None
        }
        
        # SAM模型用于对象分割
        self.sam_predictor = None
    
    def _check_dependencies(self):
        """检查Qwen图像编辑依赖"""
        if not self.qwen_available:
            raise ImportError(
                "图像编辑功能需要额外依赖，请运行: pip install -r requirements-image.txt"
            )
    
    def load_pipeline(self, model_type="qwen_edit"):
        """加载指定类型的图像编辑模型"""
        self._check_dependencies()
        
        if self.pipelines[model_type] is not None:
            return
        
        print(f"🔄 正在加载{model_type}图像编辑模型...")
        
        try:
            if model_type == "qwen_edit":
                self.pipelines[model_type] = QwenImageEditPipeline.from_pretrained(
                    "Qwen/Qwen-Image-Edit",
                    torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
                    use_safetensors=True
                )
            elif model_type == "inpaint":
                self.pipelines[model_type] = StableDiffusionInpaintPipeline.from_pretrained(
                    "runwayml/stable-diffusion-inpainting",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            elif model_type == "inpaint_xl":
                self.pipelines[model_type] = StableDiffusionXLInpaintPipeline.from_pretrained(
                    "diffusers/stable-diffusion-xl-1.0-inpainting-0.1",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            elif model_type == "controlnet_inpaint":
                controlnet = ControlNetModel.from_pretrained(
                    "lllyasviel/control_v11p_sd15_inpaint",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.pipelines[model_type] = StableDiffusionControlNetInpaintPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    controlnet=controlnet,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            
            if self.device == "cuda":
                self.pipelines[model_type] = self.pipelines[model_type].to(self.device)
            
            # 设置进度条
            self.pipelines[model_type].set_progress_bar_config(disable=None)
            
            print(f"✅ {model_type}图像编辑模型加载完成，使用设备: {self.device}")
            
        except Exception as e:
            print(f"❌ {model_type}模型加载失败: {e}")
            raise e
    
    def optimize_edit_prompt(self, user_prompt: str, language: str = "zh") -> str:
        """优化图像编辑提示词"""
        if language == "zh":
            optimization_prompt = f"""
请将以下中文图像编辑描述转换为适合AI图像编辑的英文提示词：

用户描述：{user_prompt}

要求：
1. 转换为详细的英文编辑指令
2. 使用清晰、具体的动作词汇（change, convert, transform, add, remove等）
3. 包含具体的视觉描述
4. 保持编辑意图清晰明确
5. 避免模糊或抽象的描述

请只返回优化后的英文编辑提示词：
"""
        else:
            optimization_prompt = f"""
Optimize the following prompt for AI image editing:

User prompt: {user_prompt}

Requirements:
1. Make it clear and specific for image editing
2. Use precise action words (change, convert, transform, add, remove, etc.)
3. Include specific visual descriptions
4. Keep the editing intent clear
5. Avoid vague or abstract descriptions

Return only the optimized editing prompt:
"""
        
        try:
            optimized = self.llm_client.generate(
                optimization_prompt,
                max_tokens=150,
                temperature=0.3
            )
            return optimized.strip()
        except Exception as e:
            print(f"提示词优化失败，使用原始提示词: {e}")
            return user_prompt
    
    def edit_image(
        self,
        image: Union[str, Image.Image],
        edit_prompt: str,
        negative_prompt: str = "",
        true_cfg_scale: float = 4.0,
        num_inference_steps: int = 50,
        seed: int = None,
        optimize_prompt: bool = True
    ) -> Dict[str, Any]:
        """编辑图像"""
        self._check_dependencies()
        
        # 加载模型
        if self.pipelines['qwen_edit'] is None:
            self.load_pipeline('qwen_edit')
        
        # 处理输入图像
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"图像文件不存在: {image}")
            input_image = Image.open(image).convert("RGB")
            image_source = image
        else:
            input_image = image.convert("RGB")
            image_source = "PIL Image"
        
        # 优化编辑提示词
        if optimize_prompt:
            print("🔄 正在优化编辑提示词...")
            edit_prompt = self.optimize_edit_prompt(edit_prompt)
            print(f"✨ 优化后的提示词: {edit_prompt}")
        
        # 设置随机种子
        if seed is None:
            seed = np.random.randint(0, 2**32 - 1)
        
        print(f"🎨 开始编辑图像...")
        print(f"📝 编辑指令: {edit_prompt}")
        print(f"🎯 原图尺寸: {input_image.size}")
        
        try:
            # 准备输入参数
            inputs = {
                "image": input_image,
                "prompt": edit_prompt,
                "generator": torch.manual_seed(seed),
                "true_cfg_scale": true_cfg_scale,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
            }
            
            # 执行图像编辑
            with torch.inference_mode():
                output = self.pipelines['qwen_edit'](**inputs)
                edited_image = output.images[0]
            
            # 保存编辑后的图像
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"edited_{timestamp}_seed_{seed}.png"
            output_path = os.path.join(self.output_dir, filename)
            edited_image.save(output_path)
            
            result = {
                "original_image": input_image,
                "edited_image": edited_image,
                "output_path": output_path,
                "metadata": {
                    "image_source": image_source,
                    "edit_prompt": edit_prompt,
                    "negative_prompt": negative_prompt,
                    "true_cfg_scale": true_cfg_scale,
                    "num_inference_steps": num_inference_steps,
                    "seed": seed,
                    "original_size": input_image.size,
                    "edited_size": edited_image.size,
                    "edited_at": datetime.now().isoformat()
                }
            }
            
            print(f"✅ 图像编辑完成!")
            print(f"📁 保存路径: {output_path}")
            
            return result
            
        except Exception as e:
            print(f"❌ 图像编辑失败: {e}")
            raise e
    
    def batch_edit_images(
        self,
        images: List[Union[str, Image.Image]],
        edit_prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """批量编辑图像"""
        results = []
        failed_images = []
        
        for i, image in enumerate(images):
            print(f"\n🔄 编辑第 {i+1}/{len(images)} 张图片")
            
            try:
                result = self.edit_image(image, edit_prompt, **kwargs)
                results.append({
                    "index": i,
                    "image_source": image if isinstance(image, str) else f"PIL Image {i}",
                    "result": result
                })
            except Exception as e:
                print(f"❌ 第 {i+1} 张图片编辑失败: {e}")
                failed_images.append({
                    "index": i,
                    "image_source": image if isinstance(image, str) else f"PIL Image {i}",
                    "error": str(e)
                })
        
        return {
            "successful_results": results,
            "failed_images": failed_images,
            "total_processed": len(images),
            "success_count": len(results),
            "failure_count": len(failed_images)
        }
    
    def perspective_transform(
        self,
        image: Union[str, Image.Image], 
        target_view: str,
        **kwargs
    ) -> Dict[str, Any]:
        """视角转换"""
        view_prompts = self.editing_templates["视角转换"]
        
        if target_view in view_prompts:
            edit_prompt = view_prompts[target_view]
        else:
            edit_prompt = f"Change the perspective view to {target_view}, clear and detailed"
        
        print(f"🔄 执行视角转换: {target_view}")
        return self.edit_image(image, edit_prompt, **kwargs)
    
    def style_transform(
        self,
        image: Union[str, Image.Image],
        target_style: str,
        **kwargs
    ) -> Dict[str, Any]:
        """风格转换"""
        style_prompts = self.editing_templates["风格转换"]
        
        if target_style in style_prompts:
            edit_prompt = style_prompts[target_style]
        else:
            edit_prompt = f"Convert the image to {target_style} style"
        
        print(f"🎨 执行风格转换: {target_style}")
        return self.edit_image(image, edit_prompt, **kwargs)
    
    def environment_transform(
        self,
        image: Union[str, Image.Image],
        target_environment: str,
        **kwargs
    ) -> Dict[str, Any]:
        """环境变换"""
        env_prompts = self.editing_templates["环境变换"]
        
        if target_environment in env_prompts:
            edit_prompt = env_prompts[target_environment]
        else:
            edit_prompt = f"Change the environment to {target_environment}"
        
        print(f"🌍 执行环境变换: {target_environment}")
        return self.edit_image(image, edit_prompt, **kwargs)
    
    def object_transform(
        self,
        image: Union[str, Image.Image],
        transform_type: str,
        transform_value: str,
        **kwargs
    ) -> Dict[str, Any]:
        """对象变换"""
        obj_prompts = self.editing_templates["对象变换"]
        
        if transform_type in obj_prompts:
            # 替换模板中的占位符
            if "{color}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(color=transform_value)
            elif "{material}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(material=transform_value)
            elif "{size}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(size=transform_value)
            elif "{decoration}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(decoration=transform_value)
            elif "{expression}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(expression=transform_value)
            elif "{pose}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(pose=transform_value)
            elif "{clothing}" in obj_prompts[transform_type]:
                edit_prompt = obj_prompts[transform_type].format(clothing=transform_value)
            else:
                edit_prompt = obj_prompts[transform_type]
        else:
            edit_prompt = f"Change the {transform_type} to {transform_value}"
        
        print(f"🔧 执行对象变换: {transform_type} -> {transform_value}")
        return self.edit_image(image, edit_prompt, **kwargs)
    
    def create_comparison_grid(
        self,
        original_image: Image.Image,
        edited_images: List[Image.Image],
        labels: List[str] = None
    ) -> Image.Image:
        """创建编辑前后对比网格"""
        all_images = [original_image] + edited_images
        all_labels = ["原图"] + (labels or [f"编辑 {i+1}" for i in range(len(edited_images))])
        
        # 计算网格大小
        cols = min(3, len(all_images))
        rows = (len(all_images) + cols - 1) // cols
        
        # 统一图像尺寸
        target_size = (512, 512)
        resized_images = [img.resize(target_size, Image.Resampling.LANCZOS) for img in all_images]
        
        # 创建网格画布
        grid_width = cols * target_size[0]
        grid_height = rows * target_size[1] + 50 * rows  # 为标签留出空间
        grid_image = Image.new('RGB', (grid_width, grid_height), color='white')
        
        # 粘贴图像到网格
        for idx, (image, label) in enumerate(zip(resized_images, all_labels)):
            row = idx // cols
            col = idx % cols
            
            x = col * target_size[0]
            y = row * (target_size[1] + 50)
            
            grid_image.paste(image, (x, y))
            
            # 添加标签（简单实现，实际应用中可使用PIL.ImageDraw.text）
            # 这里只是示例，实际标签需要更复杂的文字渲染
        
        return grid_image
    
    def cleanup_model(self, model_type=None):
        """清理模型释放显存"""
        if model_type is None:
            # 清理所有模型
            for key, pipeline in self.pipelines.items():
                if pipeline is not None:
                    del pipeline
                    self.pipelines[key] = None
            print("🧹 所有编辑模型已清理，显存已释放")
        else:
            # 清理指定模型
            if self.pipelines.get(model_type) is not None:
                del self.pipelines[model_type]
                self.pipelines[model_type] = None
                print(f"🧹 {model_type}编辑模型已清理，显存已释放")
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def load_sam_model(self):
        """加载SAM分割模型"""
        if not SAM_AVAILABLE:
            print("⚠️ SAM依赖未安装，无法使用对象分割功能")
            return False
        
        if self.sam_predictor is not None:
            return True
        
        try:
            print("🔄 正在加载SAM分割模型...")
            model_type = "vit_h"  # 或 vit_l, vit_b
            sam = sam_model_registry[model_type](checkpoint="sam_vit_h_4b8939.pth")
            sam.to(device=self.device)
            self.sam_predictor = SamPredictor(sam)
            print("✅ SAM分割模型加载完成")
            return True
        except Exception as e:
            print(f"❌ SAM模型加载失败: {e}")
            return False
    
    def generate_avatar(
        self,
        avatar_type: str,
        description: str = "",
        style: str = "realistic",
        **kwargs
    ) -> Dict[str, Any]:
        """虚拟形象生成"""
        # 加载生成模型
        self.load_pipeline('qwen_edit')
        
        avatar_prompts = self.editing_templates["虚拟形象生成"]
        
        if avatar_type in avatar_prompts:
            base_prompt = avatar_prompts[avatar_type]
        else:
            base_prompt = f"Generate {avatar_type} avatar"
        
        # 组合描述
        if description:
            prompt = f"{base_prompt}, {description}"
        else:
            prompt = base_prompt
            
        print(f"👤 开始生成虚拟形象: {avatar_type}")
        print(f"📝 生成描述: {prompt}")
        
        # 创建基础画布
        canvas = Image.new('RGB', (512, 512), color=(255, 255, 255))
        
        return self.edit_image(canvas, prompt, **kwargs)
    
    def ai_remove(
        self,
        image: Union[str, Image.Image],
        remove_type: str,
        target_object: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """AI消除功能"""
        # 加载修复模型
        self.load_pipeline('inpaint')
        
        remove_prompts = self.editing_templates["AI消除"]
        
        if remove_type in remove_prompts:
            if "{object}" in remove_prompts[remove_type]:
                prompt = remove_prompts[remove_type].format(object=target_object)
            else:
                prompt = remove_prompts[remove_type]
        else:
            prompt = f"Remove {remove_type} from the image"
        
        print(f"🗑️ 执行AI消除: {remove_type}")
        if target_object:
            print(f"🎯 目标对象: {target_object}")
        
        # 处理输入图像
        if isinstance(image, str):
            input_image = Image.open(image).convert("RGB")
        else:
            input_image = image.convert("RGB")
        
        # 生成掩码 - 这里需要更复杂的实现
        # 简化版本：创建基础掩码
        mask = Image.new('L', input_image.size, 0)
        
        try:
            # 使用inpainting模型
            with torch.inference_mode():
                result = self.pipelines['inpaint'](
                    prompt="",  # 空提示词表示移除
                    image=input_image,
                    mask_image=mask,
                    generator=torch.manual_seed(kwargs.get('seed', 42)),
                    **{k: v for k, v in kwargs.items() if k in ['num_inference_steps', 'guidance_scale']}
                )
                edited_image = result.images[0]
            
            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_removed_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)
            edited_image.save(output_path)
            
            return {
                "original_image": input_image,
                "edited_image": edited_image,
                "output_path": output_path,
                "metadata": {
                    "operation": "ai_remove",
                    "remove_type": remove_type,
                    "target_object": target_object,
                    "edited_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            print(f"❌ AI消除失败: {e}")
            raise e
    
    def ai_redraw(
        self,
        image: Union[str, Image.Image],
        redraw_type: str,
        description: str,
        **kwargs
    ) -> Dict[str, Any]:
        """AI重绘功能"""
        # 加载重绘模型
        self.load_pipeline('inpaint_xl')
        
        redraw_prompts = self.editing_templates["AI重绘"]
        
        if redraw_type in redraw_prompts:
            if any(placeholder in redraw_prompts[redraw_type] for placeholder in ['{description}', '{background}', '{features}', '{new_object}', '{style}']):
                prompt = redraw_prompts[redraw_type].format(
                    description=description,
                    background=description,
                    features=description,
                    new_object=description,
                    style=description
                )
            else:
                prompt = f"{redraw_prompts[redraw_type]}, {description}"
        else:
            prompt = f"Redraw {redraw_type} as {description}"
        
        print(f"🎨 执行AI重绘: {redraw_type}")
        print(f"📝 重绘描述: {description}")
        
        return self.edit_image(image, prompt, **kwargs)
    
    def virtual_scene(
        self,
        image: Union[str, Image.Image],
        scene_type: str,
        scene_elements: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """虚拟场景生成"""
        scene_prompts = self.editing_templates["虚拟场景"]
        
        if scene_type in scene_prompts:
            if "{period}" in scene_prompts[scene_type]:
                prompt = scene_prompts[scene_type].format(period=scene_elements)
            elif "{elements}" in scene_prompts[scene_type]:
                prompt = scene_prompts[scene_type].format(elements=scene_elements)
            elif "{room_type}" in scene_prompts[scene_type]:
                prompt = scene_prompts[scene_type].format(room_type=scene_elements)
            else:
                prompt = scene_prompts[scene_type]
        else:
            prompt = f"Transform into {scene_type} scene"
        
        if scene_elements and "{" not in scene_prompts.get(scene_type, ""):
            prompt = f"{prompt} with {scene_elements}"
        
        print(f"🌍 生成虚拟场景: {scene_type}")
        
        return self.edit_image(image, prompt, **kwargs)
    
    def outfit_simulation(
        self,
        image: Union[str, Image.Image],
        outfit_type: str,
        outfit_details: str,
        **kwargs
    ) -> Dict[str, Any]:
        """穿搭模拟功能"""
        outfit_prompts = self.editing_templates["穿搭模拟"]
        
        if outfit_type in outfit_prompts:
            prompt = outfit_prompts[outfit_type].format(
                clothing_style=outfit_details,
                accessories=outfit_details,
                hairstyle=outfit_details,
                makeup_style=outfit_details,
                color_theme=outfit_details,
                season=outfit_details
            )
        else:
            prompt = f"Change {outfit_type} to {outfit_details}"
        
        print(f"👗 执行穿搭模拟: {outfit_type}")
        print(f"👔 穿搭详情: {outfit_details}")
        
        return self.edit_image(image, prompt, **kwargs)
    
    def text_design(
        self,
        image: Union[str, Image.Image],
        text_type: str,
        text_content: str,
        font_style: str = "modern",
        **kwargs
    ) -> Dict[str, Any]:
        """文字设计功能"""
        text_prompts = self.editing_templates["文字设计"]
        
        if text_type in text_prompts:
            prompt = text_prompts[text_type].format(
                text=text_content,
                font_style=font_style,
                title=text_content,
                logo_text=text_content,
                calligraphy_style=font_style
            )
        else:
            prompt = f"Add {text_type} text '{text_content}' with {font_style} style"
        
        print(f"📝 执行文字设计: {text_type}")
        print(f"✏️ 文字内容: {text_content}")
        
        return self.edit_image(image, prompt, **kwargs)
    
    def poster_design(
        self,
        image: Union[str, Image.Image],
        poster_type: str,
        theme: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """海报编辑功能"""
        poster_prompts = self.editing_templates["海报编辑"]
        
        if poster_type in poster_prompts:
            if "{theme}" in poster_prompts[poster_type]:
                prompt = poster_prompts[poster_type].format(theme=theme)
            elif "{event_type}" in poster_prompts[poster_type]:
                prompt = poster_prompts[poster_type].format(event_type=theme)
            else:
                prompt = poster_prompts[poster_type]
        else:
            prompt = f"Design {poster_type} poster"
        
        if theme and "{" not in poster_prompts.get(poster_type, ""):
            prompt = f"{prompt} with {theme} theme"
        
        print(f"🎪 设计海报: {poster_type}")
        if theme:
            print(f"🎨 主题: {theme}")
        
        return self.edit_image(image, prompt, **kwargs)
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """获取可用的编辑模板"""
        templates = {}
        for category, prompts in self.editing_templates.items():
            templates[category] = list(prompts.keys())
        return templates