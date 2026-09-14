#!/usr/bin/env python3
"""Run non-network checks that keep the teaching examples discoverable.

The script deliberately parses source files instead of importing them, so it
does not need model weights, API keys, or running local services.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path


REQUIRED_FILES = (
    "README.md",
    "AutoGen/README.md",
    "Chainlit/README.md",
    "Chainlit/config.example.json",
    "GraphRAG/README.md",
    "app case/README.md",
    "langchain_QA/README.md",
    "debug/README.md",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"缺少教学文件：{relative_path}")

    config_example = root / "Chainlit/config.example.json"
    if config_example.is_file():
        try:
            json.loads(config_example.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"配置模板不是有效 JSON：{exc}")

    for source_file in root.rglob("*.py"):
        if ".git" in source_file.parts or "__pycache__" in source_file.parts:
            continue
        try:
            ast.parse(source_file.read_bytes(), filename=str(source_file))
        except SyntaxError as exc:
            failures.append(
                f"Python 语法错误：{source_file.relative_to(root)}:{exc.lineno}: {exc.msg}"
            )

    if failures:
        print("教学案例检查失败：")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("教学案例静态检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
