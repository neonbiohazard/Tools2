"""Utilities for loading and calling the base language model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import BASE_MODEL_PATH, DEVICE


@dataclass
class LLM:
    """Wrapper around a HuggingFace causal language model."""

    model_path: str | None = None

    def __post_init__(self) -> None:
        path = self.model_path or str(BASE_MODEL_PATH)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(
            path, torch_dtype=torch.float16, device_map="auto"
        ).to(DEVICE)

    def __call__(self, prompt: str, max_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                top_p=0.95,
                temperature=0.7,
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
