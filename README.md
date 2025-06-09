# Agentic Bot Framework

This repository provides a starting point for building a local agentic system that
can interact with your workspace files, plan actions, and use large language
models for text generation and tool selection.

The agent loads two models from local paths by default:

- **DeepSeek-R1-0528-Qwen3-8B** – base generation model.
- **Qwen3-Reranker-0.6B** – reranker used to select tools.

All configuration is done in `src/config.py`. Modify the model paths there to
match your environment.

Run the example chat loop:

```bash
python -m src.agent
```

This will load the models and start an interactive session where the agent can
execute dozens of workspace tools. The tool set now covers planning, code
analysis, refactoring, data inspection, dependency management and more. The
agent uses a reranker model to choose which tool best matches your request.
