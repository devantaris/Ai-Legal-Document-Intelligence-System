"""Unit tests for eval.scoring — pure math, no database."""

from eval.scoring import (
    aggregate,
    bootstrap_ci,
    char_overlap,
    merge_spans_by_file,
    span_precision_recall,
)


def test_merge_spans_unions_overlapping_and_adjacent():
    retrieved = [("a.txt", (0, 100)), ("a.txt", (80, 200)), ("a.txt", (200, 300))]
    assert merge_spans_by_file(retrieved) == [("a.txt", (0, 300))]


def test_merge_spans_keeps_gaps_and_files_separate():
    retrieved = [("a.txt", (0, 100)), ("b.txt", (0, 50)), ("a.txt", (200, 300))]
    assert merge_spans_by_file(retrieved) == [
        ("a.txt", (0, 100)),
        ("a.txt", (200, 300)),
        ("b.txt", (0, 50)),
    ]


def test_merged_retrieval_cannot_exceed_full_recall():
    # two overlapping retrieved snippets both covering the gold span
    gold = [("a.txt", (0, 100))]
    retrieved = [("a.txt", (0, 150)), ("a.txt", (50, 200))]
    merged = merge_spans_by_file(retrieved)
    assert span_precision_recall(merged, gold) == (100 / 200, 1.0)


def test_char_overlap_basics():
    assert char_overlap((0, 10), (5, 15)) == 5
    assert char_overlap((0, 10), (10, 20)) == 0  # adjacent, not overlapping
    assert char_overlap((0, 10), (0, 10)) == 10
    assert char_overlap((0, 10), (20, 30)) == 0


def test_exact_match_is_perfect():
    gold = [("a.txt", (0, 100))]
    assert span_precision_recall(gold, gold) == (1.0, 1.0)


def test_partial_overlap():
    retrieved = [("a.txt", (0, 50))]
    gold = [("a.txt", (25, 100))]
    precision, recall = span_precision_recall(retrieved, gold)
    assert precision == 0.5  # 25 of 50 retrieved chars relevant
    assert recall == 25 / 75  # 25 of 75 gold chars covered


def test_wrong_file_counts_nothing():
    retrieved = [("other.txt", (0, 100))]
    gold = [("a.txt", (0, 100))]
    assert span_precision_recall(retrieved, gold) == (0.0, 0.0)


def test_empty_retrieved_is_zero_not_error():
    gold = [("a.txt", (0, 100))]
    assert span_precision_recall([], gold) == (0.0, 0.0)


def test_overlap_sums_across_disjoint_gold_snippets():
    gold = [("a.txt", (0, 10)), ("a.txt", (20, 30))]
    retrieved = [("a.txt", (5, 25))]  # hits 5 chars of first, 5 of second
    precision, recall = span_precision_recall(retrieved, gold)
    assert precision == 10 / 20
    assert recall == 10 / 20


def test_aggregate_weights_benchmarks_equally():
    rows = [
        {"benchmark": "a", "precision": 1.0, "recall": 1.0},
        {"benchmark": "a", "precision": 0.0, "recall": 0.0},
        {"benchmark": "b", "precision": 1.0, "recall": 0.5},
    ]
    out = aggregate(rows)
    # precision: a mean 0.5, b 1.0 -> 0.75; recall: a mean 0.5, b 0.5 -> 0.5
    assert out["overall"]["precision_mean"] == 0.75
    assert out["overall"]["recall_mean"] == 0.5
    assert out["overall"]["recall_min"] == 0.0
    assert out["benchmarks"]["a"]["n_queries"] == 2
    assert out["benchmarks"]["b"]["recall_min"] == 0.5


def test_bootstrap_ci_is_tight_for_constant_values():
    lo, hi = bootstrap_ci([0.7] * 50, n_boot=200)
    assert lo == 0.7 and hi == 0.7
