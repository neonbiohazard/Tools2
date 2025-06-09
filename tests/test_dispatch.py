import sys
import types
from pathlib import Path

# Stub heavy modules
sys.modules.setdefault("torch", types.ModuleType("torch"))
transformers_stub = types.ModuleType("transformers")
transformers_stub.AutoModelForCausalLM = object
transformers_stub.AutoTokenizer = object
sys.modules.setdefault("transformers", transformers_stub)
mat_stub = types.ModuleType("matplotlib")
mat_stub.pyplot = types.ModuleType("pyplot")
sys.modules.setdefault("matplotlib", mat_stub)
sys.modules.setdefault("matplotlib.pyplot", mat_stub.pyplot)
ollama_stub = types.ModuleType("ollama")
class DummyOllamaClient:
    def generate(self, *args, **kwargs):
        return types.SimpleNamespace(text="stub")
ollama_stub.Client = DummyOllamaClient
ollama_stub.OllamaClient = DummyOllamaClient
sys.modules.setdefault("ollama", ollama_stub)

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.agent import ToolDispatcher
from src import tools

class DummyReranker:
    def __init__(self, pick_last=False):
        self.pick_last = pick_last

    def rank(self, query, options):
        scores = [0.0] * len(options)
        if self.pick_last:
            scores[-1] = 1.0
        else:
            scores[0] = 1.0
        return scores

def _dummy(path: str = ""):  # pragma: no cover
    return "dummy"

def test_dispatch():
    tools.TOOL_REGISTRY.clear()
    tools.register_tool("dummy_tool", "Dummy tool")(_dummy)
    dispatcher = ToolDispatcher(DummyReranker())
    result, name = dispatcher.dispatch("use dummy")
    assert result == "dummy"
    assert name == "dummy_tool"


def test_dispatch_none():
    tools.TOOL_REGISTRY.clear()
    tools.register_tool("dummy_tool", "Dummy tool")(_dummy)
    dispatcher = ToolDispatcher(DummyReranker(pick_last=True))
    result, name = dispatcher.dispatch("nothing")
    assert result is None and name is None


