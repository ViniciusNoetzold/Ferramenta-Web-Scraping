import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.models.schemas import ContentNode
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class AIService:
    def __init__(self):
        self.nvidia_client = None
        self.groq_client = None
        
        if settings.NVIDIA_API_KEY:
            self.nvidia_client = AsyncOpenAI(
                base_url='https://integrate.api.nvidia.com/v1',
                api_key=settings.NVIDIA_API_KEY
            )
        
        if settings.GROK_API_KEY:
            self.groq_client = AsyncOpenAI(
                base_url='https://api.groq.com/openai/v1',
                api_key=settings.GROK_API_KEY
            )

    async def _call_llm(self, messages: List[Dict[str, str]], response_format: Optional[Any] = None) -> Optional[str]:
        if self.nvidia_client and settings.NVIDIA_MODEL:
            try:
                kwargs = {"model": settings.NVIDIA_MODEL, "messages": messages}
                if response_format:
                    kwargs["response_format"] = response_format
                response = await self.nvidia_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"NVIDIA API failed: {e}. Falling back to Groq.")
        
        if self.groq_client and settings.GROK_MODEL:
            try:
                kwargs = {"model": settings.GROK_MODEL, "messages": messages}
                if response_format:
                    kwargs["response_format"] = response_format
                response = await self.groq_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API failed: {e}")
        
        return None

    async def classify_sections(self, content: List[ContentNode]) -> List[ContentNode]:
        if not self.nvidia_client and not self.groq_client:
            return content
            
        content_json = json.dumps([n.model_dump() for n in content])
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Classify the semantic sections of the given ContentNode JSON list and return the improved JSON list. ONLY return valid JSON. Do not invent any data."},
            {"role": "user", "content": content_json}
        ]
        
        result = await self._call_llm(messages, response_format={"type": "json_object"})
        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, dict) and 'data' in parsed:
                    parsed = parsed['data']
                if isinstance(parsed, list):
                    return [ContentNode(**n) for n in parsed]
            except Exception as e:
                logger.error(f"Failed to parse LLM response for classify_sections: {e}")
        return content

    async def describe_image(self, image_url: str, context: str) -> str:
        if not self.nvidia_client and not self.groq_client:
            return ""
            
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Generate a brief description for an image based on its URL and context. Do not invent anything not implied by the context/url."},
            {"role": "user", "content": f"Image URL: {image_url}\nContext: {context}"}
        ]
        
        result = await self._call_llm(messages)
        return result.strip() if result else ""

    async def detect_duplicates(self, content: List[ContentNode]) -> List[dict]:
        if not self.nvidia_client and not self.groq_client:
            return []
            
        content_json = json.dumps([{"text": n.text, "tag": n.tag} for n in content if n.text])
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Find duplicate or near-duplicate sections in the given JSON content. Return a JSON list of dictionaries with keys 'original' and 'duplicate'. ONLY return valid JSON."},
            {"role": "user", "content": content_json}
        ]
        
        result = await self._call_llm(messages, response_format={"type": "json_object"})
        if result:
            try:
                parsed = json.loads(result)
                if isinstance(parsed, dict) and 'data' in parsed:
                    parsed = parsed['data']
                if isinstance(parsed, list):
                    return parsed
            except Exception as e:
                logger.error(f"Failed to parse LLM response for detect_duplicates: {e}")
        return []

    async def generate_index(self, content: List[ContentNode]) -> str:
        if not self.nvidia_client and not self.groq_client:
            return ""
            
        content_json = json.dumps([{"text": n.text, "tag": n.tag} for n in content if n.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]])
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Create a table of contents based on the given headings. Return ONLY the markdown table of contents."},
            {"role": "user", "content": content_json}
        ]
        
        result = await self._call_llm(messages)
        return result.strip() if result else ""
