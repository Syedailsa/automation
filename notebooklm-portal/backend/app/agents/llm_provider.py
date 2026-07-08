import json
import os
import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class LLMResponse:
    def __init__(self, content: str, provider: str, model: str):
        self.content = content
        self.provider = provider
        self.model = model


class LLMProvider:
    PROVIDER_ORDER = ["cerebras", "openrouter", "openai", "anthropic", "fireworks", "ollama"]

    # Fallback models for OpenRouter when primary is rate-limited
    OPENROUTER_FALLBACK_MODELS = [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "openai/gpt-4o-mini",
    ]

    PROVIDER_ENDPOINTS = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model_env": None,
            "default_model": "meta-llama/llama-3.3-70b-instruct:free",
            "api_key_env": "OPENROUTER_API_KEY",
        },
        "openai": {
            "url": "https://api.openai.com/v1/chat/completions",
            "model_env": None,
            "default_model": "gpt-4",
            "api_key_env": "OPENAI_API_KEY",
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "model_env": None,
            "default_model": "claude-3-opus-20240229",
            "api_key_env": "ANTHROPIC_API_KEY",
        },
        "fireworks": {
            "url": "https://api.fireworks.ai/inference/v1/chat/completions",
            "model_env": None,
            "default_model": "accounts/fireworks/models/mixtral-8x22b",
            "api_key_env": "FIREWORKS_API_KEY",
        },
        "ollama": {
            "url": None,
            "model_env": "OLLAMA_MODEL",
            "default_model": "llama2",
            "api_key_env": None,
        },
        "cerebras": {
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "model_env": None,
            "default_model": "zai-glm-4.7",
            "api_key_env": "CEREBRAS_API_KEY",
        },
    }

    def __init__(self, provider: Optional[str] = None):
        self.default_provider = provider or settings.LLM_DEFAULT_PROVIDER
        self.fallback_order = self._build_fallback_order()
        self.max_retries = settings.LLM_MAX_RETRIES
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def _build_fallback_order(self) -> List[str]:
        order = []
        if self.default_provider in self.PROVIDER_ORDER:
            order.append(self.default_provider)
        configured = os.getenv("LLM_FALLBACK_PROVIDERS", settings.LLM_FALLBACK_PROVIDERS)
        for p in configured.split(","):
            p = p.strip()
            if p and p not in order:
                order.append(p)
        for p in self.PROVIDER_ORDER:
            if p not in order:
                order.append(p)
        return order

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        last_error = None
        providers_to_try = [provider] if provider else self.fallback_order

        for prov in providers_to_try:
            if prov not in self.PROVIDER_ENDPOINTS:
                continue
            # Skip providers without API keys
            cfg = self.PROVIDER_ENDPOINTS[prov]
            api_key_env = cfg.get("api_key_env", "")
            if api_key_env:
                api_key = getattr(settings, api_key_env, "") or ""
                if not api_key:
                    logger.debug(f"Skipping {prov}: no API key")
                    continue
            logger.info(f"Trying provider: {prov}")
            try:
                response = await self._try_provider(prov, prompt, system_prompt, model)
                logger.info(f"Success with provider: {prov}")
                return response.content
            except Exception as e:
                logger.warning(f"Provider {prov} failed: {type(e).__name__}: {e}")
                last_error = e
                continue

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMResponse:
        last_error = None
        providers_to_try = [provider] if provider else self.fallback_order

        for prov in providers_to_try:
            if prov not in self.PROVIDER_ENDPOINTS:
                continue
            # Skip providers without API keys
            cfg = self.PROVIDER_ENDPOINTS[prov]
            api_key_env = cfg.get("api_key_env", "")
            if api_key_env:
                api_key = getattr(settings, api_key_env, "") or ""
                if not api_key:
                    continue
            try:
                return await self._try_provider_with_messages(prov, messages, model)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(
            f"All LLM providers failed. Last error: {last_error}"
        )

    async def _try_provider(
        self, provider: str, prompt: str, system_prompt: str, model: Optional[str]
    ) -> LLMResponse:
        if provider == "ollama":
            return await self._ollama_generate(prompt, system_prompt, model)
        return await self._http_chat_completion(provider, prompt, system_prompt, model)

    async def _try_provider_with_messages(
        self, provider: str, messages: List[Dict[str, str]], model: Optional[str]
    ) -> LLMResponse:
        if provider == "ollama":
            return await self._ollama_chat(messages, model)
        return await self._http_chat_completion_with_messages(provider, messages, model)

    def _get_provider_config(self, provider: str, model: Optional[str] = None) -> dict:
        cfg = self.PROVIDER_ENDPOINTS[provider].copy()
        if model:
            cfg["default_model"] = model
        # Use settings for API keys to ensure .env values are loaded
        api_key_attr = cfg.get("api_key_env", "")
        if api_key_attr:
            cfg["api_key"] = getattr(settings, api_key_attr, "") or ""
        else:
            cfg["api_key"] = ""
        return cfg

    async def _http_chat_completion(
        self, provider: str, prompt: str, system_prompt: str, model: Optional[str]
    ) -> LLMResponse:
        cfg = self._get_provider_config(provider, model)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self._call_chat_api(provider, cfg, messages)

    async def _http_chat_completion_with_messages(
        self, provider: str, messages: List[Dict[str, str]], model: Optional[str]
    ) -> LLMResponse:
        cfg = self._get_provider_config(provider, model)
        return await self._call_chat_api(provider, cfg, messages)

    async def _call_chat_api(
        self, provider: str, cfg: dict, messages: List[Dict[str, str]]
    ) -> LLMResponse:
        import httpx

        headers = {
            "Content-Type": "application/json",
        }
        if cfg["api_key"]:
            if provider == "openrouter":
                headers["Authorization"] = f"Bearer {cfg['api_key']}"
                headers["HTTP-Referer"] = "https://novaai.8.jugaar.ai"
            else:
                headers["Authorization"] = f"Bearer {cfg['api_key']}"

        if provider == "anthropic":
            headers["x-api-key"] = cfg["api_key"]
            headers["anthropic-version"] = "2023-06-01"

        url = cfg["url"]
        timeout = httpx.Timeout(self.timeout)

        # Build list of models to try (primary + fallbacks for OpenRouter)
        models_to_try = [cfg["default_model"]]
        if provider == "openrouter":
            for m in self.OPENROUTER_FALLBACK_MODELS:
                if m not in models_to_try:
                    models_to_try.append(m)

        last_error = None
        for model_name in models_to_try:
            body: Dict[str, Any] = {
                "model": model_name,
                "messages": messages,
                "max_tokens": 4096,
            }

            if provider == "anthropic":
                system_msg = None
                chat_messages = []
                for m in messages:
                    if m["role"] == "system":
                        system_msg = m["content"]
                    else:
                        chat_messages.append(m)
                body = {
                    "model": model_name,
                    "max_tokens": 4096,
                    "messages": chat_messages,
                }
                if system_msg:
                    body["system"] = system_msg

            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        resp = await client.post(url, headers=headers, json=body)
                        resp.raise_for_status()
                        data = resp.json()

                    if provider == "anthropic":
                        content = data["content"][0]["text"]
                    else:
                        content = data["choices"][0]["message"]["content"]

                    return LLMResponse(
                        content=content,
                        provider=provider,
                        model=model_name,
                    )
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        # Rate limited — try next model
                        last_error = e
                        logger.warning(f"Model {model_name} rate-limited, trying next...")
                        break  # Break retry loop, try next model
                    last_error = e
                    if attempt < self.max_retries - 1:
                        wait = 2 ** attempt
                        await asyncio.sleep(wait)
                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        wait = 2 ** attempt
                        await asyncio.sleep(wait)

        raise RuntimeError(
            f"All LLM models failed. Last error: {last_error}"
        )

    async def _ollama_generate(
        self, prompt: str, system_prompt: str, model: Optional[str]
    ) -> LLMResponse:
        import httpx

        cfg = self._get_provider_config("ollama", model)
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        timeout = httpx.Timeout(self.timeout)

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(
                        f"{base_url}/api/generate",
                        json={
                            "model": cfg["default_model"],
                            "prompt": prompt,
                            "system": system_prompt,
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return LLMResponse(
                        content=data["response"],
                        provider="ollama",
                        model=cfg["default_model"],
                    )
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

    async def _ollama_chat(
        self, messages: List[Dict[str, str]], model: Optional[str]
    ) -> LLMResponse:
        import httpx

        cfg = self._get_provider_config("ollama", model)
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        timeout = httpx.Timeout(self.timeout)

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(
                        f"{base_url}/api/chat",
                        json={"model": cfg["default_model"], "messages": messages},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return LLMResponse(
                        content=data["message"]["content"],
                        provider="ollama",
                        model=cfg["default_model"],
                    )
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise


def build_chat_model(provider: Optional[str] = None, model: Optional[str] = None):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    prov = provider or settings.LLM_DEFAULT_PROVIDER
    cfg = LLMProvider.PROVIDER_ENDPOINTS.get(prov, {})
    api_key_env = cfg.get("api_key_env", "")
    api_key = getattr(settings, api_key_env, "") or "" if api_key_env else ""
    model_name = model or cfg.get("default_model", "gpt-4")

    if prov == "ollama":
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(model=model_name)
        except ImportError:
            return None

    base_url = None
    if prov == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
    elif prov == "fireworks":
        base_url = "https://api.fireworks.ai/inference/v1"

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/Syedailsa/automation"
        } if prov == "openrouter" else None,
    )
