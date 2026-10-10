"""Character-level precision/recall over retrieved vs gold spans.

Definitions mirror LegalBench-RAG (Pipitone & Alami, 2024, arXiv:2408.10343,
MIT licensed): for one query, with retrieved and gold snippets as
``(file_path, span)`` pairs,

    hits      = sum over retrieved snippets of their character overlap with
                every gold snippet on the same file
    precision = hits / total retrieved characters
    recall    = hits / total gold characters

Gold snippets are disjoint per file, so the numerator is well defined. A run
scores one ranked list per query and truncates it at each k in the sweep.

One deviation, documented: retrieved spans are union-merged per file before
scoring (:func:`merge_spans_by_file`). For non-overlapping retrievers — the
official baselines — this is exactly equivalent to the official formula; it
matters only when retrieved snippets overlap (our chunker emits overlapping
windows for oversized sections), where the raw formula would double-count the
same gold characters and can push recall above 1.
"""

from collections import defaultdict
from typing import Iterable


def char_overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def merge_spans_by_file(
    retrieved: Iterable[tuple[str, tuple[int, int]]],
) -> list[tuple[str, tuple[int, int]]]:
    """Union overlapping/adjacent spans per file, preserving file identity."""
    by_file: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for file_path, span in retrieved:
        by_file[file_path].append(span)
    merged: list[tuple[str, tuple[int, int]]] = []
    for file_path, spans in by_file.items():
        spans.sort()
        current = spans[0]
        for start, end in spans[1:]:
            if start <= current[1]:
                current = (current[0], max(current[1], end))
            else:
                merged.append((file_path, current))
                current = (start, end)
        merged.append((file_path, current))
    return merged


def span_precision_recall(
    retrieved: Iterable[tuple[str, tuple[int, int]]],
    gold: Iterable[tuple[str, tuple[int, int]]],
) -> tuple[float, float]:
    gold_list = list(gold)
    hits = 0
    retrieved_len = 0
    for file_path, span in retrieved:
        retrieved_len += span[1] - span[0]
        for gold_path, gold_span in gold_list:
            if file_path == gold_path:
                hits += char_overlap(span, gold_span)
    gold_len = sum(span[1] - span[0] for _, span in gold_list)
    precision = hits / retrieved_len if retrieved_len else 0.0
    recall = hits / gold_len if gold_len else 0.0
    return precision, recall


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def aggregate(rows: list[dict]) -> dict:
    """Aggregate per-query score rows into per-benchmark and overall figures.

    Each row: ``{"benchmark": str, "precision": float, "recall": float}``.
    Mirrors the official weighting: benchmarks contribute equally (0.25 each
    for the four official benchmarks), queries within a benchmark uniformly.
    Overall min-recall is over all queries; per-benchmark min-recall too.
    """
    by_benchmark: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_benchmark[row["benchmark"]].append(row)

    benchmarks: dict[str, dict] = {}
    for name, bench_rows in sorted(by_benchmark.items()):
        precisions = [r["precision"] for r in bench_rows]
        recalls = [r["recall"] for r in bench_rows]
        benchmarks[name] = {
            "n_queries": len(bench_rows),
            "precision_mean": mean(precisions),
            "recall_mean": mean(recalls),
            "recall_min": min(recalls) if recalls else float("nan"),
        }

    bench_precisions = [b["precision_mean"] for b in benchmarks.values()]
    bench_recalls = [b["recall_mean"] for b in benchmarks.values()]
    all_recalls = [r["recall"] for r in rows]
    return {
        "benchmarks": benchmarks,
        "overall": {
            "n_queries": len(rows),
            "precision_mean": mean(bench_precisions),
            "recall_mean": mean(bench_recalls),
            "recall_min": min(all_recalls) if all_recalls else float("nan"),
        },
    }


def bootstrap_ci(
    values: list[float],
    *,
    n_boot: int = 1000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean, in pure Python (no numpy dep)."""
    import random

    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)
    stats = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        stats.append(sum(sample) / n)
    stats.sort()
    alpha = (1.0 - confidence) / 2.0
    lo = stats[max(0, int(alpha * n_boot))]
    hi = stats[min(n_boot - 1, int((1.0 - alpha) * n_boot) - 1)]
    return (lo, hi)
