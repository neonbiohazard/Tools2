"""Interactive agent that uses an LLM and a reranker to call tools."""
from __future__ import annotations

import argparse

import inspect
import json
import re
from pathlib import Path

from .llm import LLM
from .reranker import Reranker
from . import tools


class ChatHistory:
    """Persist conversation history for better context."""

    def __init__(self, path: str = "history.json", max_entries: int = 20) -> None:
        self.path = Path(path)
        if self.path.exists():
            self.entries = json.loads(self.path.read_text())
        else:
            self.entries = []
        self.max_entries = max_entries

    def add(self, speaker: str, text: str) -> None:
        self.entries.append({"speaker": speaker, "text": text})
        self.entries = self.entries[-self.max_entries :]
        self.path.write_text(json.dumps(self.entries, indent=2))

    def context(self) -> str:
        return "\n".join(f"{e['speaker']}: {e['text']}" for e in self.entries)


class ToolDispatcher:
    """Select and execute tools using a reranker."""

    def __init__(self, reranker: Reranker):
        self.reranker = reranker

    # Match Windows (C:\path or C:/path) and POSIX (/path or ./path) style paths
    PATH_RE = re.compile(
        r"([A-Za-z]:[\\/][^\s]+|\.\/?[^\s]+|/[\w./-]+)"
    )

    def _parse_args(self, tool: str, query: str) -> dict:
        match = self.PATH_RE.search(query)
        kwargs: dict = {}
        if match:
            kwargs["path"] = match.group(1)
            if tool == "list_dir" and ("recursive" in query or "all" in query):
                kwargs["recursive"] = True
        return kwargs

    def dispatch(self, query: str):
        options = list(tools.available_tools().keys()) + ["none"]
        descriptions = list(tools.available_tools().values()) + ["No tool"]
        scores = self.reranker.rank(query, descriptions)
        best = options[scores.index(max(scores))]
        if best == "none":
            tools.log_tool_usage("none", "no action")
            return None, None
        kwargs = self._parse_args(best, query)
        func, _ = tools.TOOL_REGISTRY[best]
        sig = inspect.signature(func)
        required = [
            p.name
            for p in sig.parameters.values()
            if p.default is inspect._empty and p.kind == p.POSITIONAL_OR_KEYWORD
        ]
        if any(name not in kwargs for name in required):
            tools.log_tool_usage(best, "missing arguments")
            return None, None
        try:
            result = func(**kwargs)
        except Exception as e:
            result = f"Tool {best} failed: {e}"
        tools.log_tool_usage(best, str(result))
        return result, best


def chat_loop():
    llm = LLM()
    reranker = Reranker()
    dispatcher = ToolDispatcher(reranker)
    history = ChatHistory()
    if not history.entries:
        system_msg = (
            "You are a helpful local assistant with access to workspace tools. "
            "Call tools when useful and respond with clear answers."
        )
        history.add("System", system_msg)

    print("Agent ready. Type 'exit' to quit.")
    while True:
        user = input("User> ")
        if user.strip().lower() == "exit":
            break

        history.add("User", user)
        res, tool = dispatcher.dispatch(user)
        if res is not None:
            print("[Tool]", res)
            history.add("Tool", f"{tool}: {res}")
        prompt = history.context() + "\nAssistant:"
        response = llm(prompt)
        history.add("Assistant", response)
        print(response)


if __name__ == "__main__":
    chat_loop()
