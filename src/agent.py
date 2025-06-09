"""Interactive agent that uses an LLM and a reranker to call tools."""
from __future__ import annotations

import argparse
from typing import List

from .llm import LLM
from .reranker import Reranker
from . import tools


class ToolDispatcher:
    """Select and execute tools using a reranker."""

    def __init__(self, reranker: Reranker):
        self.reranker = reranker

    def dispatch(self, query: str, *args, **kwargs):
        options = list(tools.available_tools().keys())
        descriptions = list(tools.available_tools().values())
        scores = self.reranker.rank(query, descriptions)
        best = options[scores.index(max(scores))]
        return tools.dispatch_tool(best, *args, **kwargs)


def chat_loop():
    llm = LLM()
    reranker = Reranker()
    dispatcher = ToolDispatcher(reranker)

    print("Agent ready. Type 'exit' to quit.")
    while True:
        user = input("User> ")
        if user.strip().lower() == "exit":
            break

        # Simple heuristic: if user seems to ask about files, try to use a tool
        if "folder" in user or "file" in user:
            try:
                result = dispatcher.dispatch(user)
                print("[Tool]", result)
            except Exception as e:
                print("[Tool error]", e)
                result = ""
        else:
            result = ""

        prompt = f"User: {user}\n{result}\nAssistant:"
        response = llm(prompt)
        print(response)


if __name__ == "__main__":
    chat_loop()
