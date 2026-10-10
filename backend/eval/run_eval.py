"""M1 retrieval evaluation over LegalBench-RAG (docs/paper-plan.md, section 4).

Forces the eval stack before any app import: isolated `legal_ai_eval` database,
Ollama + nomic-embed-text embeddings (768-dim). Dev data and dev .env settings
are never used.

Usage (from backend/):
  .venv/Scripts/python -m eval.run_eval \
      --data-dir ../benchmark_data/legalbenchrag/lbr \
      --benchmarks contractnli cuad maud privacy_qa \
      --ks 1,2,4,8,16,32,64 --channels hybrid

Results land in <repo>/eval_results/<timestamp>_<channels>.json (gitignored),
including per-query ranked spans for later error analysis.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

EVAL_DB_NAME = "legal_ai_eval"


def _configure_env() -> None:
    """Isolated DB + local embedding stack, BEFORE app modules are imported."""
    probe = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://legal:legal@localhost:5433/legal_ai",
    )
    os.environ["DATABASE_URL"] = probe.rsplit("/", 1)[0] + f"/{EVAL_DB_NAME}"
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["OLLAMA_EMBED_MODEL"] = "nomic-embed-text"
    os.environ["EMBEDDING_DIM"] = "768"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="LegalBench-RAG data dir containing benchmarks/ and corpus/",
    )
    p.add_argument(
        "--benchmarks",
        nargs="+",
        default=["contractnli", "cuad", "maud", "privacy_qa"],
    )
    p.add_argument("--ks", default="1,2,4,8,16,32,64", help="comma-separated k values")
    p.add_argument(
        "--channels",
        choices=["hybrid", "vector", "fts"],
        default="hybrid",
        help="retrieval channels (ablation switch)",
    )
    p.add_argument(
        "--max-tests",
        type=int,
        default=194,
        help="official protocol caps at 194 tests per benchmark",
    )
    p.add_argument("--limit", type=int, default=None, help="smoke-test query cap")
    p.add_argument(
        "--fresh",
        action="store_true",
        help="re-chunk and re-embed even if documents already exist",
    )
    p.add_argument("--out", type=Path, default=None, help="override output path")
    return p.parse_args(argv)


def _ensure_database() -> None:
    import sqlalchemy as sa

    from app.core.config import settings
    from app.core.database import Base, engine

    admin_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            exists = conn.execute(
                sa.text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": EVAL_DB_NAME},
            ).scalar()
            if not exists:
                conn.execute(sa.text(f'CREATE DATABASE "{EVAL_DB_NAME}"'))
    finally:
        admin.dispose()
    with engine.connect() as conn:
        conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    ks = [int(k) for k in args.ks.split(",")]
    channels = {"hybrid": None, "vector": {"vector"}, "fts": {"fts"}}[args.channels]
    pool = max(ks)

    _configure_env()
    from app.core.config import settings

    from eval.adapter import LegalIQRetrieval
    from eval.lbr import check_gold_spans, load_corpus, load_queries, used_file_paths
    from eval.scoring import aggregate, merge_spans_by_file, span_precision_recall

    print(f"eval db: {settings.DATABASE_URL.rsplit('/', 1)[-1]}")
    print(f"embed: {settings.OLLAMA_EMBED_MODEL} dim={settings.EMBEDDING_DIM}")
    _ensure_database()

    queries = load_queries(
        args.data_dir, args.benchmarks, max_tests_per_benchmark=args.max_tests
    )
    if args.limit:
        queries = queries[: args.limit]
    file_paths = used_file_paths(queries)
    corpus = load_corpus(args.data_dir, file_paths)
    bad_spans = check_gold_spans(corpus, queries)
    print(
        f"queries: {len(queries)}  corpus files: {len(corpus)}  "
        f"chars: {sum(len(c) for c in corpus.values()) / 1e6:.1f}M  "
        f"bad gold spans: {bad_spans}"
    )
    if bad_spans:
        print("aborting: gold spans out of bounds indicate a corpus decoding problem")
        return 2

    from app.core.database import SessionLocal

    method = LegalIQRetrieval(channels=channels)
    with SessionLocal() as db:
        method.ensure_user(db)
    print(f"ingesting (channels={args.channels}) ...")
    stats = method.ingest_corpus(corpus, fresh=args.fresh)
    print(
        f"ingest: {stats['docs']} docs, {stats['reused_docs']} reused, "
        f"{stats['embedded_chunks']} chunks embedded in {stats['embed_seconds']}s"
    )

    per_query_rows: list[dict] = []
    started = time.perf_counter()
    for i, q in enumerate(queries):
        ranked = method.ranked_spans(q.query, top_k=pool)
        ranked_items = [
            {
                "file_path": r.filename,
                "span": list(method.span_of(r) or (0, 0)),
                "score": r.score,
            }
            for r in ranked
        ]
        gold = [(s.file_path, s.span) for s in q.snippets]
        row = {
            "query_id": q.query_id,
            "benchmark": q.benchmark,
            "n_gold_snippets": len(gold),
            "ranked": ranked_items,
            "scores": {},
        }
        for k in ks:
            precision, recall = span_precision_recall(
                merge_spans_by_file(
                    [(item["file_path"], tuple(item["span"])) for item in ranked_items[:k]]
                ),
                gold,
            )
            row["scores"][str(k)] = {"precision": precision, "recall": recall}
        per_query_rows.append(row)
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(queries)} queries scored "
                  f"({time.perf_counter() - started:.0f}s)")

    results = {
        "run": {
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "benchmarks": args.benchmarks,
            "channels": args.channels,
            "ks": ks,
            "max_tests_per_benchmark": args.max_tests,
            "query_limit": args.limit,
            "chunk_tokens": settings.CHUNK_TOKENS,
            "chunk_overlap_tokens": settings.CHUNK_OVERLAP_TOKENS,
            "embed_model": settings.OLLAMA_EMBED_MODEL,
            "embedding_dim": settings.EMBEDDING_DIM,
            "ingest": {k: v for k, v in stats.items()},
            "rerank": "none",
        },
        "per_benchmark": {},
        "queries": per_query_rows,
    }
    for k in ks:
        rows = [
            {
                "benchmark": r["benchmark"],
                "precision": r["scores"][str(k)]["precision"],
                "recall": r["scores"][str(k)]["recall"],
            }
            for r in per_query_rows
        ]
        results["per_benchmark"][str(k)] = aggregate(rows)

    out_path = args.out or (
        Path(__file__).resolve().parents[2]
        / "eval_results"
        / f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{args.channels}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=1), encoding="utf-8")

    print(f"\nresults written to {out_path}\n")
    header = (
        f"{'benchmark':<12}" + "".join(
            f"| k={k:<4}{'recall':>8}{'prec':>8}" for k in ks
        )
    )
    print(header)
    bench_names = sorted(
        {r["benchmark"] for r in per_query_rows}
    )
    for name in bench_names:
        cells = []
        for k in ks:
            b = results["per_benchmark"][str(k)]["benchmarks"].get(name)
            cells.append(
                f"|      {100 * b['recall_mean']:>5.1f}%{100 * b['precision_mean']:>7.1f}%"
            )
        print(f"{name:<12}" + "".join(cells))
    overall = "".join(
        f"|      {100 * results['per_benchmark'][str(k)]['overall']['recall_mean']:>5.1f}%"
        f"{100 * results['per_benchmark'][str(k)]['overall']['precision_mean']:>7.1f}%"
        for k in ks
    )
    print(f"{'OVERALL':<12}" + overall)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
