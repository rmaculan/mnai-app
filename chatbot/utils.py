from deepseek import DeepSeekAPI
from openai import OpenAI
import os

class AIProvider:
    def chat_completion(self, messages):
        raise NotImplementedError

class OpenAIProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)

    def chat_completion(self, messages):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response

class DeepSeekProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        self.client = DeepSeekAPI(api_key=api_key)

    def chat_completion(self, messages):
        # Convert OpenAI format messages to DeepSeek format
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        system_prompt = next((m['content'] for m in messages if m['role'] == 'system'), None)
        
        response = self.client.chat_completion(
            prompt=prompt,
            prompt_sys=system_prompt or "You are a helpful AI assistant",
            model='deepseek-chat',
            stream=False
        )
        return response

def get_provider(provider_name="openai"):
    """Factory method to get AI provider instance"""
    providers = {
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unsupported provider: {provider_name}")
        
    return providers[provider_name]()
