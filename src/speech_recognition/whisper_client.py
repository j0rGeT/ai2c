import os
import whisper
from typing import Dict, Any, Optional
from datetime import datetime
import tempfile
from pydub import AudioSegment

class WhisperClient:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self.output_dir = "./outputs/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_model(self):
        if self.model is None:
            print(f"加载Whisper模型: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
    
    def transcribe_audio(self, audio_path: str, language: str = "zh") -> Dict[str, Any]:
        self.load_model()
        
        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=False,
                verbose=True
            )
            
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"],
                "duration": self._get_audio_duration(audio_path)
            }
        except Exception as e:
            raise Exception(f"音频转录失败: {str(e)}")
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = "zh") -> Dict[str, Any]:
        self.load_model()
        
        result = self.model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            fp16=False
        )
        
        formatted_segments = []
        for segment in result["segments"]:
            formatted_segments.append({
                "start_time": self._format_time(segment["start"]),
                "end_time": self._format_time(segment["end"]),
                "text": segment["text"].strip(),
                "confidence": segment.get("avg_logprob", 0)
            })
        
        return {
            "full_text": result["text"],
            "segments": formatted_segments,
            "language": result["language"],
            "duration": self._get_audio_duration(audio_path)
        }
    
    def convert_audio_format(self, input_path: str, output_format: str = "wav") -> str:
        try:
            audio = AudioSegment.from_file(input_path)
            
            output_path = os.path.join(
                self.output_dir,
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_converted.{output_format}"
            )
            
            audio.export(output_path, format=output_format)
            return output_path
        except Exception as e:
            raise Exception(f"音频格式转换失败: {str(e)}")
    
    def split_audio(self, audio_path: str, chunk_duration_ms: int = 300000) -> list:
        try:
            audio = AudioSegment.from_file(audio_path)
            chunks = []
            
            for i, chunk_start_ms in enumerate(range(0, len(audio), chunk_duration_ms)):
                chunk_end_ms = chunk_start_ms + chunk_duration_ms
                chunk = audio[chunk_start_ms:chunk_end_ms]
                
                chunk_path = os.path.join(
                    self.output_dir,
                    f"chunk_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                )
                
                chunk.export(chunk_path, format="wav")
                chunks.append(chunk_path)
            
            return chunks
        except Exception as e:
            raise Exception(f"音频分割失败: {str(e)}")
    
    def transcribe_long_audio(self, audio_path: str, language: str = "zh", chunk_duration_ms: int = 300000) -> Dict[str, Any]:
        chunk_paths = self.split_audio(audio_path, chunk_duration_ms)
        
        all_text = []
        all_segments = []
        current_offset = 0
        
        try:
            for i, chunk_path in enumerate(chunk_paths):
                print(f"处理第 {i+1}/{len(chunk_paths)} 个音频片段")
                
                chunk_result = self.transcribe_with_timestamps(chunk_path, language)
                all_text.append(chunk_result["full_text"])
                
                for segment in chunk_result["segments"]:
                    segment["start_time"] = self._add_time_offset(segment["start_time"], current_offset)
                    segment["end_time"] = self._add_time_offset(segment["end_time"], current_offset)
                    all_segments.append(segment)
                
                current_offset += chunk_duration_ms / 1000
                
                os.remove(chunk_path)
            
            return {
                "full_text": " ".join(all_text),
                "segments": all_segments,
                "language": language,
                "total_chunks": len(chunk_paths)
            }
        except Exception as e:
            for chunk_path in chunk_paths:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
            raise e
    
    def _get_audio_duration(self, audio_path: str) -> float:
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            return 0.0
    
    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def _add_time_offset(self, time_str: str, offset_seconds: float) -> str:
        parts = time_str.split(":")
        total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        total_seconds += offset_seconds
        return self._format_time(total_seconds)