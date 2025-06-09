# Agentic Bot Framework

This repository provides a starting point for building a local agentic system that
can interact with your workspace files, plan actions, and use large language
models for text generation and tool selection.

The agent loads two models from local paths by default:

- **DeepSeek-R1-0528-Qwen3-8B** – base generation model.
- **Qwen3-Reranker-0.6B** – reranker used to select tools.

All configuration is done in `src/config.py`. Modify the model paths there to
match your environment. Models are loaded with CUDA acceleration (tested on a
3090) by default; change the `DEVICE` setting if you need CPU execution.

Run the example chat loop:

```bash
python -m src.agent
```

This will load the models and start an interactive session. You can converse as
with any chatbot. For each user message the agent consults a reranker to decide
whether a tool should be run. If a suitable tool is found it executes it and
shows the result before replying. Otherwise it simply answers with the language
model. The tool set covers planning, code analysis, refactoring, data
inspection, dependency management and more. Tool functions self-register via a
``@register_tool`` decorator, making it easy to extend the system. Conversation
history is stored in ``history.json`` so the LLM can reference earlier
exchanges.

### Folder summaries

The ``summarize_folder`` tool chains ``list_dir`` and ``summarize_file`` to
provide a quick overview of each file in a directory. Ask the agent something
like ``"Can you summarize the folder at ./src?"`` and it will inspect and
summarize a few files for you.

### Natural interaction

Because the dispatcher always runs, you can simply ask the assistant anything.
For example:

```
User> How many rows are in data.csv?
[Tool] Rows: 100, Columns: 5
Assistant: The CSV has 100 rows and five columns.
```
