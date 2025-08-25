import os
from datetime import datetime
from typing import Dict, Any, Optional
from .llm_client import LLMClient

class ContentGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.output_dir = "./outputs/articles"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_article(self, topic: str, style: str = "informative", length: str = "medium", provider: str = None) -> Dict[str, Any]:
        length_mapping = {
            "short": "500-800字",
            "medium": "1000-1500字",
            "long": "2000-3000字"
        }
        
        style_mapping = {
            "informative": "信息性和教育性的",
            "narrative": "叙述性和故事性的",
            "persuasive": "说服性和观点性的",
            "technical": "技术性和专业性的",
            "casual": "轻松和对话式的"
        }
        
        prompt = f"""
请根据以下要求写一篇文章：

主题：{topic}
风格：{style_mapping.get(style, style)}
长度：{length_mapping.get(length, length)}

要求：
1. 文章结构清晰，包含引言、正文和结论
2. 内容原创，观点明确
3. 语言流畅，逻辑清晰
4. 适当使用标题和段落分隔
5. 确保内容准确且有价值

请直接输出文章内容：
"""
        
        content = self.llm_client.generate(prompt, provider=provider, max_tokens=3000)
        
        result = {
            "title": f"关于{topic}的文章",
            "content": content,
            "metadata": {
                "topic": topic,
                "style": style,
                "length": length,
                "provider": provider,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(content)
            }
        }
        
        return result
    
    def generate_novel_chapter(self, plot: str, characters: str = "", setting: str = "", chapter_number: int = 1, provider: str = None) -> Dict[str, Any]:
        prompt = f"""
请根据以下设定写一章小说：

章节编号：第{chapter_number}章
剧情概要：{plot}
"""
        
        if characters:
            prompt += f"主要人物：{characters}\n"
        if setting:
            prompt += f"背景设定：{setting}\n"
        
        prompt += """
要求：
1. 章节长度约2000-3000字
2. 情节发展合理，有起伏
3. 人物性格鲜明，对话自然
4. 描写生动，有画面感
5. 保持故事的连贯性和吸引力
6. 章节结尾要有悬念或转折

请直接输出章节内容：
"""
        
        content = self.llm_client.generate(prompt, provider=provider, max_tokens=4000, temperature=0.8)
        
        result = {
            "title": f"第{chapter_number}章",
            "content": content,
            "metadata": {
                "chapter_number": chapter_number,
                "plot": plot,
                "characters": characters,
                "setting": setting,
                "provider": provider,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(content)
            }
        }
        
        return result
    
    def generate_story_outline(self, theme: str, genre: str = "现代", length: str = "中篇", provider: str = None) -> Dict[str, Any]:
        prompt = f"""
请为小说创作一个详细的大纲：

主题：{theme}
类型：{genre}
长度：{length}

请包含以下内容：
1. 故事概述（200字左右）
2. 主要人物设定（3-5个主角，包括姓名、性格、背景）
3. 背景设定（时间、地点、社会背景等）
4. 章节大纲（8-12章，每章简要情节）
5. 主要冲突和转折点
6. 结局设定

请以结构化的方式输出：
"""
        
        content = self.llm_client.generate(prompt, provider=provider, max_tokens=3000)
        
        result = {
            "title": f"{theme}小说大纲",
            "content": content,
            "metadata": {
                "theme": theme,
                "genre": genre,
                "length": length,
                "provider": provider,
                "generated_at": datetime.now().isoformat()
            }
        }
        
        return result
    
    def save_content(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{result['title'][:20].replace(' ', '_')}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {result['title']}\n\n")
            f.write(f"{result['content']}\n\n")
            f.write("---\n\n")
            f.write("## 元数据\n")
            for key, value in result['metadata'].items():
                f.write(f"- **{key}**: {value}\n")
        
        return filepath