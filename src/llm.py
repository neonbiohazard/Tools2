"""Utilities for calling the generation model via Ollama."""
from __future__ import annotations

from dataclasses import dataclass

from ollama import Client as OllamaClient

from .config import OLLAMA_MODEL_NAME


@dataclass
class LLM:
    """Ollama-backed language model."""

    model_name: str = OLLAMA_MODEL_NAME

    def __post_init__(self) -> None:
        self.client = OllamaClient()

    def __call__(self, prompt: str, max_tokens: int = 256) -> str:
        resp = self.client.generate(
            self.model_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
        )
        return resp.text
