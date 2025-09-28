# services/llm_service.py
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        self.session = None

    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """
        Generate response using local LLM (Ollama)
        """
        try:
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9
                }
            }

            async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    logger.error(f"LLM API error: {response.status}")
                    return ""
                    
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""

    async def extract_json(self, text: str, schema_description: str) -> Dict[str, Any]:
        """
        Extract structured JSON from text using LLM
        """
        system_prompt = f"""
        Extract structured data as JSON based on this schema: {schema_description}
        Return only valid JSON, no additional text.
        """
        
        response = await self.generate_response(system_prompt, text)
        
        try:
            # Try to parse JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
            
        return {}

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
