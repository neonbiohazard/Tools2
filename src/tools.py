"""Core workspace tools available to the agent."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable, Tuple


def read_file(path: str | Path) -> str:
    """Return the contents of ``path`` as text."""
    return Path(path).read_text()


def write_file(path: str | Path, content: str) -> None:
    """Write ``content`` to ``path``, overwriting if it exists."""
    Path(path).write_text(content)


def append_file(path: str | Path, content: str) -> None:
    """Append ``content`` to ``path``."""
    with Path(path).open("a") as f:
        f.write(content)


def delete_file(path: str | Path) -> None:
    Path(path).unlink(missing_ok=True)


def list_dir(path: str | Path, recursive: bool = False) -> list[str]:
    base = Path(path)
    if recursive:
        return [str(p) for p in base.rglob("*")]
    return [str(p) for p in base.iterdir()]


def move_file(src: str | Path, dest: str | Path) -> None:
    shutil.move(str(src), str(dest))


def copy_file(src: str | Path, dest: str | Path) -> None:
    shutil.copy2(str(src), str(dest))


def summarize_file(path: str | Path) -> str:
    """Very naive summarization by returning the first few lines."""
    text = Path(path).read_text().splitlines()
    return "\n".join(text[:20])


def generate_readme(path: str | Path) -> None:
    """Create a README file summarizing files in ``path``."""
    entries = list_dir(path, recursive=True)
    content = "# Project Files\n\n" + "\n".join(f"- {e}" for e in entries)
    write_file(Path(path) / "README.generated.md", content)


# Map of tool name -> (callable, description)
TOOL_REGISTRY: dict[str, Tuple[callable, str]] = {
    "read_file": (read_file, "Read and return file contents"),
    "write_file": (write_file, "Write text to a file"),
    "append_file": (append_file, "Append text to a file"),
    "delete_file": (delete_file, "Delete a file"),
    "list_dir": (list_dir, "List directory contents"),
    "move_file": (move_file, "Move a file"),
    "copy_file": (copy_file, "Copy a file"),
    "summarize_file": (summarize_file, "Return a short summary of a file"),
    "generate_readme": (generate_readme, "Generate a README listing files"),
}


def available_tools() -> dict[str, str]:
    """Return mapping of tool names to descriptions."""
    return {name: desc for name, (_, desc) in TOOL_REGISTRY.items()}


def dispatch_tool(name: str, *args, **kwargs):
    """Execute a tool by name."""
    func, _ = TOOL_REGISTRY[name]
    return func(*args, **kwargs)
