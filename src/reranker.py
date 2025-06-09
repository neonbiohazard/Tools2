"""Tool selection reranker using a language model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .config import RERANKER_MODEL_PATH, DEVICE


@dataclass
class Reranker:
    """Ranks tool options based on their relevance to a query."""

    model_path: str | None = None

    def __post_init__(self) -> None:
        path = self.model_path or str(RERANKER_MODEL_PATH)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(
            path, torch_dtype=torch.float16, device_map=DEVICE
        )

    def rank(self, query: str, options: Iterable[str]) -> List[float]:
        scores = []
        for opt in options:
            prompt = f"[INST]Which is more relevant to: '{query}'?\nOption: {opt}[/INST]"
            inputs = self.tokenizer(prompt, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                out = self.model(**inputs, labels=inputs.input_ids)
                # Use negative loss as a crude log-prob score
                score = -out.loss.item()
            scores.append(score)
        return scores
