import os
from typing import Optional


class LLMProvider:
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY")
    
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self.provider == "openai":
            return await self._openai_generate(prompt, system_prompt)
        elif self.provider == "anthropic":
            return await self._anthropic_generate(prompt, system_prompt)
        elif self.provider == "ollama":
            return await self._ollama_generate(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _openai_generate(self, prompt: str, system_prompt: str) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            return response.json()["choices"][0]["message"]["content"]
    
    async def _anthropic_generate(self, prompt: str, system_prompt: str) -> str:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            return response.json()["content"][0]["text"]
    
    async def _ollama_generate(self, prompt: str, system_prompt: str) -> str:
        import httpx
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "system": system_prompt
                }
            )
            return response.json()["response"]
