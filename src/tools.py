"""Core workspace tools available to the agent."""
from __future__ import annotations

import json
import shutil
import subprocess
import ast
import csv
from pathlib import Path
from typing import Iterable, Tuple, Any

import matplotlib.pyplot as plt


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


# ---------------------------------------------------------------------------
# Reasoning & Planning Tools
# ---------------------------------------------------------------------------

def create_design_doc(goal: str) -> str:
    """Create a simple design document for a goal."""
    doc = f"# Design Document\n\n## Goal\n{goal}\n"
    write_file("DESIGN_DOC.generated.md", doc)
    return doc


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


def summarize_progress() -> str:
    """Summarize project memory file if present."""
    mem = Path("project_memory.json")
    if mem.exists():
        return mem.read_text()
    return "No progress recorded."


# ---------------------------------------------------------------------------
# Code Intelligence & Static Analysis
# ---------------------------------------------------------------------------

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


def find_code_smells(path: str) -> list[str]:
    """Report long lines as a simple code smell indicator."""
    smells = []
    for i, line in enumerate(Path(path).read_text().splitlines(), 1):
        if len(line) > 120:
            smells.append(f"Line {i}: exceeds 120 chars")
    return smells


def parse_ast(path: str) -> str:
    """Return the AST of ``path`` as a string."""
    tree = ast.parse(Path(path).read_text())
    return ast.dump(tree)


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

def lint_code(path: str) -> str:
    """Run flake8 on ``path``."""
    result = subprocess.run(["flake8", path], capture_output=True, text=True)
    return result.stdout + result.stderr


def format_code(path: str) -> str:
    """Run black formatter on ``path``."""
    result = subprocess.run(["black", path, "--quiet"], capture_output=True, text=True)
    return result.stdout + result.stderr


def remove_unused_imports(path: str) -> None:
    """Remove unused imports using autoflake."""
    subprocess.run(["autoflake", "--in-place", path])


# ---------------------------------------------------------------------------
# Testing & Validation Tools
# ---------------------------------------------------------------------------

def generate_unit_tests(path: str) -> str:
    """Create a placeholder unit test for ``path``."""
    module = Path(path).stem
    test_file = Path("tests") / f"test_{module}.py"
    test_file.parent.mkdir(exist_ok=True)
    content = f"import {module}\n\n\n" "def test_placeholder():\n    assert {module}.__file__\n"
    write_file(test_file, content)
    return str(test_file)


def run_tests() -> str:
    """Run pytest if available."""
    result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    return result.stdout + result.stderr


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

def refactor_code(path: str, instructions: str) -> None:
    """Append a refactor note to ``path``."""
    append_file(path, f"\n# TODO: refactor - {instructions}\n")


def split_large_function(path: str, func_name: str) -> None:
    """Mark a function for splitting."""
    append_file(path, f"\n# TODO: split function {func_name}\n")


def merge_duplicate_functions() -> str:
    """Placeholder for merging similar functions."""
    return "TODO: merge duplicate functions"


# ---------------------------------------------------------------------------
# Data / CSV / Log Tools
# ---------------------------------------------------------------------------

def summarize_csv(path: str) -> str:
    """Return number of rows and columns of a CSV file."""
    with open(path) as f:
        reader = list(csv.reader(f))
    rows = len(reader) - 1 if reader else 0
    cols = len(reader[0]) if reader else 0
    return f"Rows: {rows}, Columns: {cols}"


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


def analyze_data_trends(path: str) -> str:
    """Placeholder for data trend analysis."""
    return f"Data trend analysis not implemented for {path}"


# ---------------------------------------------------------------------------
# Dependency Management Tools
# ---------------------------------------------------------------------------

def parse_requirements() -> list[str]:
    """Return list of dependencies from requirements.txt."""
    req = Path("requirements.txt")
    if req.exists():
        return [l.strip() for l in req.read_text().splitlines() if l.strip()]
    return []


def upgrade_all_dependencies() -> None:
    """Placeholder for upgrading dependencies."""
    append_file("requirements.txt", "\n# TODO: upgrade dependencies\n")


def check_vulnerability_report() -> str:
    """Placeholder for vulnerability scanning."""
    return "Vulnerability check not implemented"


# ---------------------------------------------------------------------------
# Documentation / Internet Tools
# ---------------------------------------------------------------------------

def search_docs(query: str) -> str:
    """Placeholder for local or web doc search."""
    return f"Search docs for '{query}' not implemented"


def fetch_docs_for(symbol: str) -> str:
    """Placeholder to fetch documentation for a symbol."""
    return f"Docs for {symbol} not available"


def search_stackoverflow(query: str) -> str:
    """Placeholder StackOverflow search."""
    return f"StackOverflow search for '{query}' not implemented"


# ---------------------------------------------------------------------------
# Utility / Meta Tools
# ---------------------------------------------------------------------------

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


def monitor_workspace_activity() -> str:
    """Placeholder for workspace monitoring."""
    return "Workspace monitoring not implemented"


def save_state(filename: str, data: Any) -> None:
    """Save ``data`` as JSON to ``filename``."""
    Path(filename).write_text(json.dumps(data, indent=2))


def load_state(filename: str) -> Any:
    """Load JSON state from ``filename``."""
    return json.loads(Path(filename).read_text())


# ---------------------------------------------------------------------------
# User Interaction Helpers
# ---------------------------------------------------------------------------

def ask_user(question: str) -> str:
    """Prompt the user and return their answer."""
    return input(question + " ")


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


def defer_decision(reason: str) -> str:
    """Return a string noting the decision was deferred."""
    return f"Decision deferred: {reason}"


# ---------------------------------------------------------------------------
# Memory Overlay Helpers
# ---------------------------------------------------------------------------

def log_tool_usage(name: str, result: str) -> None:
    """Append a tool usage record to ``tool_usage_log.json``."""
    log_file = Path("tool_usage_log.json")
    if log_file.exists():
        log = json.loads(log_file.read_text())
    else:
        log = []
    log.append({"tool": name, "result": result})
    save_state(log_file, log)


def record_project_memory(note: str) -> None:
    """Add a note to ``project_memory.json``."""
    mem_file = Path("project_memory.json")
    if mem_file.exists():
        mem = json.loads(mem_file.read_text())
    else:
        mem = []
    mem.append(note)
    save_state(mem_file, mem)



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
    # Reasoning & Planning
    "create_design_doc": (create_design_doc, "Create a design document"),
    "create_task_plan": (create_task_plan, "Create a task plan"),
    "summarize_progress": (summarize_progress, "Summarize project progress"),
    # Code Intelligence
    "detect_dead_code": (detect_dead_code, "Find unused functions in a file"),
    "find_code_smells": (find_code_smells, "Report simple code smells"),
    "parse_ast": (parse_ast, "Return AST of a Python file"),
    "list_todos": (list_todos, "List TODO/FIXME comments"),
    # Code Hygiene
    "lint_code": (lint_code, "Run flake8 on a path"),
    "format_code": (format_code, "Run black formatter"),
    "remove_unused_imports": (remove_unused_imports, "Remove unused imports"),
    # Testing & Validation
    "generate_unit_tests": (generate_unit_tests, "Generate a placeholder unit test"),
    "run_tests": (run_tests, "Run pytest tests"),
    "validate_json": (validate_json, "Validate JSON file"),
    # Refactoring
    "refactor_code": (refactor_code, "Append refactor instructions"),
    "split_large_function": (split_large_function, "Mark a function for splitting"),
    "merge_duplicate_functions": (merge_duplicate_functions, "Merge similar functions"),
    # Data / CSV
    "summarize_csv": (summarize_csv, "Summarize a CSV file"),
    "plot_csv_column": (plot_csv_column, "Plot a column from a CSV"),
    "analyze_data_trends": (analyze_data_trends, "Analyze CSV data trends"),
    # Dependencies
    "parse_requirements": (parse_requirements, "Parse requirements.txt"),
    "upgrade_all_dependencies": (upgrade_all_dependencies, "Mark deps for upgrade"),
    "check_vulnerability_report": (check_vulnerability_report, "Check for vulnerabilities"),
    # Docs / Internet
    "search_docs": (search_docs, "Search documentation"),
    "fetch_docs_for": (fetch_docs_for, "Fetch docs for a symbol"),
    "search_stackoverflow": (search_stackoverflow, "Search StackOverflow"),
    # Utility / Meta
    "generate_dockerfile": (generate_dockerfile, "Generate a Dockerfile"),
    "create_cli_wrapper": (create_cli_wrapper, "Create a CLI wrapper"),
    "monitor_workspace_activity": (monitor_workspace_activity, "Monitor workspace"),
    "save_state": (save_state, "Save JSON state"),
    "load_state": (load_state, "Load JSON state"),
    # User interaction
    "ask_user": (ask_user, "Prompt the user"),
    "offer_options": (offer_options, "Offer options to the user"),
    "defer_decision": (defer_decision, "Defer a decision"),
    # Memory helpers
    "log_tool_usage": (log_tool_usage, "Record tool usage"),
    "record_project_memory": (record_project_memory, "Record project note"),
}


def available_tools() -> dict[str, str]:
    """Return mapping of tool names to descriptions."""
    return {name: desc for name, (_, desc) in TOOL_REGISTRY.items()}


def dispatch_tool(name: str, *args, **kwargs):
    """Execute a tool by name."""
    func, _ = TOOL_REGISTRY[name]
    return func(*args, **kwargs)
