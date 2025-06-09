"""Configuration for model paths and runtime options."""

from pathlib import Path

# Update these paths to match where your models reside.
BASE_MODEL_PATH = Path(r"F:\AI\CODEX\QwenModels\DeepSeek-R1-0528-Qwen3-8B")
RERANKER_MODEL_PATH = Path(r"F:\AI\CODEX\QwenModels\Qwen3-Reranker-0.6B")

# Torch device to load models on (e.g. "cuda" or "cpu")
DEVICE = "cuda"
