import os
from typing import Optional, Dict, Any
import openai
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.deepseek_client = None
        
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        if os.getenv('DEEPSEEK_API_KEY'):
            self.deepseek_client = openai.OpenAI(
                api_key=os.getenv('DEEPSEEK_API_KEY'),
                base_url="https://api.deepseek.com"
            )
    
    def generate_with_openai(self, prompt: str, model: str = "gpt-4", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def generate_with_anthropic(self, prompt: str, model: str = "claude-3-haiku-20240307", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def generate_with_deepseek(self, prompt: str, model: str = "deepseek-chat", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        if not self.deepseek_client:
            raise ValueError("DeepSeek API key not configured")
        
        response = self.deepseek_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def generate(self, prompt: str, provider: str = None, **kwargs) -> str:
        if provider is None:
            provider = os.getenv('DEFAULT_LLM_PROVIDER', 'deepseek')
        
        if provider.lower() == "deepseek":
            return self.generate_with_deepseek(prompt, **kwargs)
        elif provider.lower() == "openai":
            return self.generate_with_openai(prompt, **kwargs)
        elif provider.lower() == "anthropic":
            return self.generate_with_anthropic(prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")