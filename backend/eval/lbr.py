"""Loading of the LegalBench-RAG benchmark data.

Data layout (official Dropbox download): ``<data_dir>/benchmarks/<name>.json``
plus ``<data_dir>/corpus/<file_path>``. Ground truth is character spans into
corpus files. MAUD file names contain ``||`` (a legal filename on Linux, where
the data was produced, but illegal on Windows) — on disk those characters are
stored as ``__``; identities keep the original strings, and all disk access
goes through :func:`disk_path`.

``load_queries`` replicates the official ``benchmark.py`` sampling: at most
194 tests per benchmark, preferring tests that share documents
(sort-by-document) so the ingested corpus stays small. The sampling is
deterministic given the data (seeded per file path).
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path

OFFICIAL_MAX_TESTS = 194


@dataclass
class GoldSnippet:
    file_path: str
    span: tuple[int, int]  # [start, end) character offsets into the corpus file


@dataclass
class GoldQuery:
    query_id: str
    benchmark: str
    query: str
    snippets: list[GoldSnippet]


def disk_path(data_dir: Path, file_path: str) -> Path:
    return data_dir / "corpus" / file_path.replace("||", "__")


def load_queries(
    data_dir: Path,
    benchmark_names: list[str],
    *,
    max_tests_per_benchmark: int = OFFICIAL_MAX_TESTS,
    sort_by_document: bool = True,
) -> list[GoldQuery]:
    queries: list[GoldQuery] = []
    for name in benchmark_names:
        raw = json.loads(
            (data_dir / "benchmarks" / f"{name}.json").read_text(encoding="utf-8")
        )
        tests = raw["tests"]
        if len(tests) > max_tests_per_benchmark:
            if sort_by_document:
                tests = sorted(
                    tests,
                    key=lambda t: (
                        random.seed(t["snippets"][0]["file_path"]),
                        random.random(),
                    )[1],
                )
            else:
                random.seed(name)
                random.shuffle(tests)
            tests = tests[:max_tests_per_benchmark]
        for i, test in enumerate(tests):
            queries.append(
                GoldQuery(
                    query_id=f"{name}::{i}",
                    benchmark=name,
                    query=test["query"],
                    snippets=[
                        GoldSnippet(s["file_path"], (s["span"][0], s["span"][1]))
                        for s in test["snippets"]
                    ],
                )
            )
    return queries


def used_file_paths(queries: list[GoldQuery]) -> list[str]:
    return sorted({s.file_path for q in queries for s in q.snippets})


def load_corpus(data_dir: Path, file_paths: list[str]) -> dict[str, str]:
    """Read the corpus files referenced by the queries.

    Files are read as UTF-8; a file that is not valid UTF-8 falls back to
    replacement decoding with a printed warning — a span-bounds check
    downstream will surface any offset drift this could cause.
    """
    corpus: dict[str, str] = {}
    for file_path in file_paths:
        path = disk_path(data_dir, file_path)
        try:
            corpus[file_path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"WARNING: non-UTF-8 corpus file, replacing bad bytes: {file_path}")
            corpus[file_path] = path.read_text(encoding="utf-8", errors="replace")
    return corpus


def check_gold_spans(corpus: dict[str, str], queries: list[GoldQuery]) -> int:
    """Verify every gold span lies within its file. Returns violation count."""
    bad = 0
    for q in queries:
        for s in q.snippets:
            content = corpus.get(s.file_path)
            if content is None:
                continue
            if not (0 <= s.span[0] < s.span[1] <= len(content)):
                bad += 1
                print(
                    f"WARNING: gold span out of bounds: {q.query_id} "
                    f"{s.file_path} {s.span} (file len {len(content)})"
                )
    return bad
