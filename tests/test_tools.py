import sys
import types
from pathlib import Path

# Stub heavy modules before importing project code
sys.modules.setdefault("torch", types.ModuleType("torch"))
matplotlib_stub = types.ModuleType("matplotlib")
matplotlib_stub.pyplot = types.ModuleType("pyplot")
sys.modules.setdefault("matplotlib", matplotlib_stub)
sys.modules.setdefault("matplotlib.pyplot", matplotlib_stub.pyplot)
ollama_stub = types.ModuleType("ollama")
class DummyOllamaClient:
    def generate(self, *args, **kwargs):
        return {"response": "stub"}
ollama_stub.Client = DummyOllamaClient
ollama_stub.OllamaClient = DummyOllamaClient
sys.modules.setdefault("ollama", ollama_stub)

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src import tools

def test_read_write(tmp_path):
    file = tmp_path / "a.txt"
    tools.write_file(file, "hello")
    assert tools.read_file(file) == "hello"
    tools.append_file(file, " world")
    assert "world" in tools.read_file(file)


def test_summarize_folder(tmp_path):
    f1 = tmp_path / "one.txt"
    f2 = tmp_path / "two.txt"
    tools.write_file(f1, "alpha")
    tools.write_file(f2, "beta")
    summary = tools.summarize_folder(tmp_path, max_files=2)
    assert "alpha" in summary and "beta" in summary
