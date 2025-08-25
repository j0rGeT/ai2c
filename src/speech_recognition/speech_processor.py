import os
from datetime import datetime
from typing import Dict, Any, Optional
from .whisper_client import WhisperClient
from ..content_generation.llm_client import LLMClient

class SpeechProcessor:
    def __init__(self):
        self.whisper_client = WhisperClient()
        self.llm_client = LLMClient()
        self.output_dir = "./outputs/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def transcribe_and_summarize(
        self, 
        audio_path: str, 
        language: str = "zh",
        summary_type: str = "详细",
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        
        print("开始音频转录...")
        transcription_result = self.whisper_client.transcribe_with_timestamps(audio_path, language)
        
        print("生成内容摘要...")
        summary = self._generate_summary(
            transcription_result["full_text"], 
            summary_type,
            language
        )
        
        markdown_content = self._format_as_markdown(
            transcription_result, 
            summary, 
            audio_path
        )
        
        result = {
            "transcription": transcription_result,
            "summary": summary,
            "markdown": markdown_content,
            "metadata": {
                "audio_file": os.path.basename(audio_path),
                "language": language,
                "duration": transcription_result.get("duration", 0),
                "summary_type": summary_type,
                "processed_at": datetime.now().isoformat()
            }
        }
        
        return result
    
    def _generate_summary(self, text: str, summary_type: str, language: str) -> Dict[str, str]:
        if language == "zh":
            summary_prompts = {
                "简要": f"请对以下文本进行简要总结（100-200字）：\n\n{text}",
                "详细": f"""请对以下文本进行详细分析和总结：

文本内容：
{text}

请提供：
1. 主要内容概述（200-300字）
2. 关键要点列表（3-5个要点）
3. 重要信息提取
4. 总结建议或行动项（如适用）

请以结构化的方式呈现：""",
                "要点": f"请提取以下文本的关键要点，以列表形式呈现：\n\n{text}",
                "会议纪要": f"""请将以下会议录音转录内容整理为正式的会议纪要：

录音内容：
{text}

请包含：
1. 会议主题和时间
2. 参会人员（如能识别）
3. 讨论要点
4. 决议事项
5. 待办事项
6. 下次会议安排（如有）

请以专业的会议纪要格式呈现："""
            }
        else:
            summary_prompts = {
                "简要": f"Please provide a brief summary (100-200 words) of the following text:\n\n{text}",
                "详细": f"""Please provide a detailed analysis and summary of the following text:

Content:
{text}

Please include:
1. Main content overview (200-300 words)
2. Key points list (3-5 points)
3. Important information extraction
4. Summary recommendations or action items (if applicable)

Please present in a structured format:""",
                "要点": f"Please extract the key points from the following text in list format:\n\n{text}",
                "会议纪要": f"""Please organize the following meeting transcription into formal meeting minutes:

Transcription content:
{text}

Please include:
1. Meeting topic and time
2. Participants (if identifiable)
3. Discussion points
4. Decisions made
5. Action items
6. Next meeting arrangements (if any)

Please present in professional meeting minutes format:"""
            }
        
        prompt = summary_prompts.get(summary_type, summary_prompts["详细"])
        
        try:
            summary_text = self.llm_client.generate(prompt, max_tokens=2000)
            
            return {
                "type": summary_type,
                "content": summary_text,
                "word_count": len(summary_text)
            }
        except Exception as e:
            return {
                "type": summary_type,
                "content": f"摘要生成失败: {str(e)}",
                "word_count": 0
            }
    
    def _format_as_markdown(
        self, 
        transcription: Dict[str, Any], 
        summary: Dict[str, str], 
        audio_path: str
    ) -> str:
        
        markdown = f"""# 音频转录和分析报告

## 基本信息
- **音频文件**: {os.path.basename(audio_path)}
- **语言**: {transcription.get('language', 'unknown')}
- **时长**: {transcription.get('duration', 0):.2f} 秒
- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 内容摘要

{summary['content']}

## 完整转录文本

{transcription['full_text']}

## 分段转录（带时间戳）

"""
        
        for i, segment in enumerate(transcription.get('segments', []), 1):
            markdown += f"**{segment['start_time']} - {segment['end_time']}**\n"
            markdown += f"{segment['text']}\n\n"
        
        markdown += """---

*本报告由AI自动生成，如有错误请以原始音频为准。*
"""
        
        return markdown
    
    def save_results(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_name = result['metadata']['audio_file'].split('.')[0]
            filename = f"{timestamp}_{audio_name}_transcript.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result['markdown'])
        
        return filepath
    
    def process_batch_audio(self, audio_files: list, **kwargs) -> Dict[str, Any]:
        results = {}
        failed_files = []
        
        for audio_file in audio_files:
            try:
                print(f"处理音频文件: {audio_file}")
                result = self.transcribe_and_summarize(audio_file, **kwargs)
                results[audio_file] = result
                
                output_path = self.save_results(result)
                print(f"结果已保存到: {output_path}")
                
            except Exception as e:
                print(f"处理 {audio_file} 时出错: {str(e)}")
                failed_files.append({"file": audio_file, "error": str(e)})
        
        return {
            "successful": results,
            "failed": failed_files,
            "total_processed": len(audio_files),
            "success_count": len(results),
            "failure_count": len(failed_files)
        }