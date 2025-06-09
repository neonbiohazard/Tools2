"""Interactive agent that uses an LLM and a reranker to call tools."""
from __future__ import annotations

import argparse

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

    PATH_RE = re.compile(r"([A-Za-z]:\\\\[\w\\\\.-]+|\.\/?[\w./-]+|/[\w./-]+)")

    def _parse_args(self, tool: str, query: str) -> dict:
        match = self.PATH_RE.search(query)
        kwargs: dict = {}
        if match:
            kwargs["path"] = match.group(1)
            if tool == "list_dir" and ("recursive" in query or "all" in query):
                kwargs["recursive"] = True
        return kwargs

    def dispatch(self, query: str):
        options = list(tools.available_tools().keys())
        descriptions = list(tools.available_tools().values())
        scores = self.reranker.rank(query, descriptions)
        best = options[scores.index(max(scores))]
        kwargs = self._parse_args(best, query)
        try:
            result = tools.dispatch_tool(best, **kwargs)
        except Exception as e:
            result = f"Tool {best} failed: {e}"
        tools.log_tool_usage(best, str(result))
        return result, best


def chat_loop():
    llm = LLM()
    reranker = Reranker()
    dispatcher = ToolDispatcher(reranker)
    history = ChatHistory()

    print("Agent ready. Type 'exit' to quit.")
    while True:
        user = input("User> ")
        if user.strip().lower() == "exit":
            break

        history.add("User", user)
        result = ""
        if "folder" in user or "file" in user:
            res, tool = dispatcher.dispatch(user)
            print("[Tool]", res)
            history.add("Tool", f"{tool}: {res}")
            result = res
        prompt = history.context() + "\nAssistant:"
        response = llm(prompt)
        history.add("Assistant", response)
        print(response)


if __name__ == "__main__":
    chat_loop()
