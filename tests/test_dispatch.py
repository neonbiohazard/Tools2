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

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.agent import ToolDispatcher
from src import tools

class DummyReranker:
    def rank(self, query, options):
        return [1.0] + [0.0]*(len(options)-1)

def _dummy(path: str = ""):  # pragma: no cover
    return "dummy"

def test_dispatch():
    tools.TOOL_REGISTRY.clear()
    tools.register_tool("dummy_tool", "Dummy tool")(_dummy)
    dispatcher = ToolDispatcher(DummyReranker())
    result, name = dispatcher.dispatch("use dummy")
    assert result == "dummy"
    assert name == "dummy_tool"


