"""Shared JSON extraction helpers for LLM structured output."""

import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Extract the first JSON value from an LLM reply.

    Handles raw JSON, ```json fences, and prose-wrapped JSON by scanning for
    the first balanced object/array while respecting string escapes.
    """
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s).strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    for open_char, close_char in (("{", "}"), ("[", "]")):
        start = s.find(open_char)
        if start == -1:
            continue
        depth = 0
        in_str = False
        escaped = False
        for i in range(start, len(s)):
            c = s[i]
            if in_str:
                if escaped:
                    escaped = False
                elif c == "\\":
                    escaped = True
                elif c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == open_char:
                    depth += 1
                elif c == close_char:
                    depth -= 1
                    if depth == 0:
                        return json.loads(s[start : i + 1])
    raise ValueError("No valid JSON found in LLM reply")
