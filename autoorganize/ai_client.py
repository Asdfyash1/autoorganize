"""Unified AI client supporting OpenAI, Gemini, and NVIDIA APIs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class AIProvider:
    name: str
    base_url: str
    api_key: str
    model: str
    headers: dict[str, str]


def _detect_provider() -> AIProvider:
    """Auto-detect available AI provider from environment variables."""
    if key := os.environ.get("OPENAI_API_KEY"):
        return AIProvider(
            name="OpenAI",
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=key,
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )

    if key := os.environ.get("GEMINI_API_KEY"):
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        return AIProvider(
            name="Gemini",
            base_url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
            api_key=key,
            model=model,
            headers={"Content-Type": "application/json"},
        )

    if key := os.environ.get("NVIDIA_API_KEY"):
        return AIProvider(
            name="NVIDIA",
            base_url="https://integrate.api.nvidia.com/v1/chat/completions",
            api_key=key,
            model=os.environ.get("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )

    raise EnvironmentError(
        "No AI API key found. Set one of: OPENAI_API_KEY, GEMINI_API_KEY, or NVIDIA_API_KEY"
    )


def query_ai(prompt: str, system_prompt: str = "", provider: Optional[AIProvider] = None) -> str:
    """Send a prompt to the AI provider and return the response text."""
    if provider is None:
        provider = _detect_provider()

    if provider.name == "Gemini":
        return _query_gemini(prompt, system_prompt, provider)
    return _query_openai_compatible(prompt, system_prompt, provider)


def _query_openai_compatible(prompt: str, system_prompt: str, provider: AIProvider) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": provider.model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(provider.base_url, headers=provider.headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _query_gemini(prompt: str, system_prompt: str, provider: AIProvider) -> str:
    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024},
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(provider.base_url, headers=provider.headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


def get_provider_name() -> str:
    try:
        return _detect_provider().name
    except EnvironmentError:
        return "none"
