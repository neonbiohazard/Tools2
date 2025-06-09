"""Configuration for model paths and runtime options."""

from pathlib import Path

# Model configuration
OLLAMA_MODEL_NAME = "qwen3:8b"  # Generation model served by Ollama
RERANKER_MODEL_PATH = Path(r"F:\AI\CODEX\QwenModels\Qwen3-Reranker-0.6B")

# Torch device for the reranker (e.g. "cuda" or "cpu")
DEVICE = "cuda"
