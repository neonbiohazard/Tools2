"""Core workspace tools available to the agent."""
from __future__ import annotations

import json
import shutil
import subprocess
import ast
import csv
from pathlib import Path
from typing import Iterable, Tuple, Any, Callable

import matplotlib.pyplot as plt

# Registry of tool functions populated via ``@register_tool``.
TOOL_REGISTRY: dict[str, Tuple[Callable, str]] = {}


def register_tool(name: str, description: str) -> Callable:
    """Decorator to register a function as an agent tool."""

    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = (func, description)
        return func

    return decorator


@register_tool("read_file", "Read and return file contents")
def read_file(path: str | Path) -> str:
    """Return the contents of ``path`` as text."""
    return Path(path).read_text()


@register_tool("write_file", "Write text to a file")
def write_file(path: str | Path, content: str) -> None:
    """Write ``content`` to ``path``, overwriting if it exists."""
    Path(path).write_text(content)


@register_tool("append_file", "Append text to a file")
def append_file(path: str | Path, content: str) -> None:
    """Append ``content`` to ``path``."""
    with Path(path).open("a") as f:
        f.write(content)


@register_tool("delete_file", "Delete a file")
def delete_file(path: str | Path) -> None:
    Path(path).unlink(missing_ok=True)


@register_tool("list_dir", "List directory contents")
def list_dir(path: str | Path, recursive: bool = False) -> list[str]:
    base = Path(path)
    if recursive:
        return [str(p) for p in base.rglob("*")]
    return [str(p) for p in base.iterdir()]


@register_tool("move_file", "Move a file")
def move_file(src: str | Path, dest: str | Path) -> None:
    shutil.move(str(src), str(dest))


@register_tool("copy_file", "Copy a file")
def copy_file(src: str | Path, dest: str | Path) -> None:
    shutil.copy2(str(src), str(dest))


@register_tool("summarize_file", "Return a short summary of a file")
def summarize_file(path: str | Path, max_lines: int = 20, use_llm: bool = False) -> str:
    """Summarize file contents using an LLM if available."""
    text = Path(path).read_text()
    if use_llm:
        try:
            from .llm import LLM

            llm = LLM()
            prompt = f"Summarize the following file:\n\n{text[:2000]}\n\nSummary:"
            return llm(prompt, max_tokens=128)
        except Exception as e:
            return f"LLM summarization failed: {e}"
    lines = text.splitlines()[:max_lines]
    return "\n".join(lines)


@register_tool("generate_readme", "Generate a README listing files")
def generate_readme(path: str | Path) -> None:
    """Create a README file summarizing files in ``path``."""
    entries = list_dir(path, recursive=True)
    content = "# Project Files\n\n" + "\n".join(f"- {e}" for e in entries)
    write_file(Path(path) / "README.generated.md", content)


@register_tool("summarize_folder", "Summarize the contents of a folder")
def summarize_folder(path: str | Path, max_files: int = 5) -> str:
    """List files and return short summaries for a subset."""
    entries = list_dir(path)
    summaries = []
    for fp in entries[:max_files]:
        p = Path(fp)
        if p.is_file():
            summ = summarize_file(p, max_lines=10)
            summaries.append(f"{p}::\n{summ}")
    return "\n\n".join(summaries)


# ---------------------------------------------------------------------------
# Reasoning & Planning Tools
# ---------------------------------------------------------------------------

@register_tool("create_design_doc", "Create a design document")
def create_design_doc(goal: str) -> str:
    """Create a simple design document for a goal."""
    doc = f"# Design Document\n\n## Goal\n{goal}\n"
    write_file("DESIGN_DOC.generated.md", doc)
    return doc


@register_tool("create_task_plan", "Create a task plan")
def create_task_plan(goal: str) -> list[str]:
    """Return a naive list of tasks to achieve ``goal``."""
    tasks = [
        f"Clarify requirements for {goal}",
        "Design solution",
        "Implement code",
        "Test and review",
    ]
    save_state("goal_stack.json", tasks)
    return tasks


@register_tool("summarize_progress", "Summarize project progress")
def summarize_progress() -> str:
    """Summarize project memory file if present."""
    mem = Path("project_memory.json")
    if mem.exists():
        return mem.read_text()
    return "No progress recorded."


# ---------------------------------------------------------------------------
# Code Intelligence & Static Analysis
# ---------------------------------------------------------------------------

@register_tool("detect_dead_code", "Find unused functions in a file")
def detect_dead_code(path: str) -> list[str]:
    """Naively report functions never called in ``path``."""
    text = Path(path).read_text()
    tree = ast.parse(text)
    defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    calls = [
        n.func.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    ]
    return [d for d in defs if d not in calls]


@register_tool("find_code_smells", "Report simple code smells")
def find_code_smells(path: str) -> list[str]:
    """Report long lines as a simple code smell indicator."""
    smells = []
    for i, line in enumerate(Path(path).read_text().splitlines(), 1):
        if len(line) > 120:
            smells.append(f"Line {i}: exceeds 120 chars")
    return smells


@register_tool("parse_ast", "Return AST of a Python file")
def parse_ast(path: str) -> str:
    """Return the AST of ``path`` as a string."""
    tree = ast.parse(Path(path).read_text())
    return ast.dump(tree)


@register_tool("list_todos", "List TODO/FIXME comments")
def list_todos(path: str) -> list[str]:
    """Find TODO or FIXME comments in ``path`` recursively."""
    todos = []
    for p in Path(path).rglob("*.py"):
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                todos.append(f"{p}:{i}:{line.strip()}")
    return todos


# ---------------------------------------------------------------------------
# Code Hygiene Tools
# ---------------------------------------------------------------------------

@register_tool("lint_code", "Run flake8 on a path")
def lint_code(path: str) -> str:
    """Run flake8 on ``path``."""
    result = subprocess.run(["flake8", path], capture_output=True, text=True)
    return result.stdout + result.stderr


@register_tool("format_code", "Run black formatter")
def format_code(path: str) -> str:
    """Run black formatter on ``path``."""
    result = subprocess.run(["black", path, "--quiet"], capture_output=True, text=True)
    return result.stdout + result.stderr


@register_tool("remove_unused_imports", "Remove unused imports")
def remove_unused_imports(path: str) -> None:
    """Remove unused imports using autoflake."""
    subprocess.run(["autoflake", "--in-place", path])


# ---------------------------------------------------------------------------
# Testing & Validation Tools
# ---------------------------------------------------------------------------

@register_tool("generate_unit_tests", "Generate a placeholder unit test")
def generate_unit_tests(path: str) -> str:
    """Create a placeholder unit test for ``path``."""
    module = Path(path).stem
    test_file = Path("tests") / f"test_{module}.py"
    test_file.parent.mkdir(exist_ok=True)
    content = f"import {module}\n\n\n" "def test_placeholder():\n    assert {module}.__file__\n"
    write_file(test_file, content)
    return str(test_file)


@register_tool("run_tests", "Run pytest tests")
def run_tests() -> str:
    """Run pytest if available."""
    result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    return result.stdout + result.stderr


@register_tool("validate_json", "Validate JSON file")
def validate_json(path: str) -> str:
    """Validate JSON file syntax."""
    try:
        json.loads(Path(path).read_text())
        return "Valid JSON"
    except Exception as e:
        return f"Invalid JSON: {e}"


# ---------------------------------------------------------------------------
# Refactoring Tools
# ---------------------------------------------------------------------------

@register_tool("refactor_code", "Append refactor instructions")
def refactor_code(path: str, instructions: str) -> None:
    """Append a refactor note to ``path``."""
    append_file(path, f"\n# TODO: refactor - {instructions}\n")


@register_tool("split_large_function", "Mark a function for splitting")
def split_large_function(path: str, func_name: str) -> None:
    """Mark a function for splitting."""
    append_file(path, f"\n# TODO: split function {func_name}\n")


@register_tool("merge_duplicate_functions", "Merge similar functions")
def merge_duplicate_functions() -> str:
    """Placeholder for merging similar functions."""
    return "TODO: merge duplicate functions"


# ---------------------------------------------------------------------------
# Data / CSV / Log Tools
# ---------------------------------------------------------------------------

@register_tool("summarize_csv", "Summarize a CSV file")
def summarize_csv(path: str) -> str:
    """Return number of rows and columns of a CSV file."""
    with open(path) as f:
        reader = list(csv.reader(f))
    rows = len(reader) - 1 if reader else 0
    cols = len(reader[0]) if reader else 0
    return f"Rows: {rows}, Columns: {cols}"


@register_tool("plot_csv_column", "Plot a column from a CSV")
def plot_csv_column(path: str, column: int) -> str:
    """Plot a CSV column and save to an image."""
    vals = []
    with open(path) as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            try:
                vals.append(float(row[column]))
            except Exception:
                pass
    plt.figure()
    plt.plot(vals)
    out = Path(path).with_suffix(f"_{column}.png")
    plt.savefig(out)
    return str(out)


@register_tool("analyze_data_trends", "Analyze CSV data trends")
def analyze_data_trends(path: str) -> str:
    """Placeholder for data trend analysis."""
    return f"Data trend analysis not implemented for {path}"


# ---------------------------------------------------------------------------
# Dependency Management Tools
# ---------------------------------------------------------------------------

@register_tool("parse_requirements", "Parse requirements.txt")
def parse_requirements() -> list[str]:
    """Return list of dependencies from requirements.txt."""
    req = Path("requirements.txt")
    if req.exists():
        return [l.strip() for l in req.read_text().splitlines() if l.strip()]
    return []


@register_tool("upgrade_all_dependencies", "Mark deps for upgrade")
def upgrade_all_dependencies() -> None:
    """Placeholder for upgrading dependencies."""
    append_file("requirements.txt", "\n# TODO: upgrade dependencies\n")


@register_tool("check_vulnerability_report", "Check for vulnerabilities")
def check_vulnerability_report() -> str:
    """Placeholder for vulnerability scanning."""
    return "Vulnerability check not implemented"


# ---------------------------------------------------------------------------
# Documentation / Internet Tools
# ---------------------------------------------------------------------------

@register_tool("search_docs", "Search documentation")
def search_docs(query: str) -> str:
    """Placeholder for local or web doc search."""
    return f"Search docs for '{query}' not implemented"


@register_tool("fetch_docs_for", "Fetch docs for a symbol")
def fetch_docs_for(symbol: str) -> str:
    """Placeholder to fetch documentation for a symbol."""
    return f"Docs for {symbol} not available"


@register_tool("search_stackoverflow", "Search StackOverflow")
def search_stackoverflow(query: str) -> str:
    """Placeholder StackOverflow search."""
    return f"StackOverflow search for '{query}' not implemented"


# ---------------------------------------------------------------------------
# Utility / Meta Tools
# ---------------------------------------------------------------------------

@register_tool("generate_dockerfile", "Generate a Dockerfile")
def generate_dockerfile(path: str) -> None:
    """Create a simple Dockerfile in ``path``."""
    content = (
        "FROM python:3.10\n"
        "WORKDIR /app\n"
        "COPY . .\n"
        "RUN pip install -r requirements.txt\n"
        "CMD [\"python\", \"-m\", \"src.agent\"]\n"
    )
    write_file(Path(path) / "Dockerfile", content)


@register_tool("create_cli_wrapper", "Create a CLI wrapper")
def create_cli_wrapper(path: str) -> None:
    """Add a minimal argparse CLI wrapper for a module."""
    mod = Path(path).stem
    wrapper = (
        "import argparse\n"
        f"import {mod}\n\n"
        "if __name__ == '__main__':\n"
        "    parser = argparse.ArgumentParser()\n"
        "    parser.add_argument('--args', nargs='*')\n"
        "    parser.parse_args()\n"
    )
    write_file(Path(path).with_suffix("_cli.py"), wrapper)


@register_tool("monitor_workspace_activity", "Monitor workspace")
def monitor_workspace_activity() -> str:
    """Placeholder for workspace monitoring."""
    return "Workspace monitoring not implemented"


@register_tool("save_state", "Save JSON state")
def save_state(filename: str, data: Any) -> None:
    """Save ``data`` as JSON to ``filename``."""
    Path(filename).write_text(json.dumps(data, indent=2))


@register_tool("load_state", "Load JSON state")
def load_state(filename: str) -> Any:
    """Load JSON state from ``filename``."""
    return json.loads(Path(filename).read_text())


# ---------------------------------------------------------------------------
# User Interaction Helpers
# ---------------------------------------------------------------------------

@register_tool("ask_user", "Prompt the user")
def ask_user(question: str) -> str:
    """Prompt the user and return their answer."""
    return input(question + " ")


@register_tool("offer_options", "Offer options to the user")
def offer_options(question: str, options: Iterable[str]) -> str:
    """Ask the user to choose from ``options``."""
    print(question)
    options = list(options)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    choice = input("Choice: ")
    try:
        idx = int(choice) - 1
        return options[idx]
    except Exception:
        return ""


@register_tool("defer_decision", "Defer a decision")
def defer_decision(reason: str) -> str:
    """Return a string noting the decision was deferred."""
    return f"Decision deferred: {reason}"


# ---------------------------------------------------------------------------
# Memory Overlay Helpers
# ---------------------------------------------------------------------------

@register_tool("log_tool_usage", "Record tool usage")
def log_tool_usage(name: str, result: str) -> None:
    """Append a tool usage record to ``tool_usage_log.json``."""
    log_file = Path("tool_usage_log.json")
    if log_file.exists():
        log = json.loads(log_file.read_text())
    else:
        log = []
    log.append({"tool": name, "result": result})
    save_state(log_file, log)


@register_tool("record_project_memory", "Record project note")
def record_project_memory(note: str) -> None:
    """Add a note to ``project_memory.json``."""
    mem_file = Path("project_memory.json")
    if mem_file.exists():
        mem = json.loads(mem_file.read_text())
    else:
        mem = []
    mem.append(note)
    save_state(mem_file, mem)






def available_tools() -> dict[str, str]:
    """Return mapping of tool names to descriptions."""
    return {name: desc for name, (_, desc) in TOOL_REGISTRY.items()}


def dispatch_tool(name: str, *args, **kwargs):
    """Execute a tool by name."""
    func, _ = TOOL_REGISTRY[name]
    return func(*args, **kwargs)
