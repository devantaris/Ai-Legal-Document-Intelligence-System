# M1 — LegalBench-RAG retrieval baseline (go/no-go gate)

**Verdict: PASSED.** The fully-local pipeline (nomic-embed-text 768-dim + Postgres FTS,
RRF-fused, structure-aware ~700-token chunks) matches or beats the paper's best published
baseline (OpenAI text-embedding-3-large, naive-500 chunks, no rerank) on recall@k for
3 of 4 datasets, at every k in the official sweep.

- Run: `eval_results/20261010_213239_hybrid.json` (776 queries, official 194-per-benchmark
  sampling, corpus restricted to the 72 referenced documents, 4,529 chunks embedded in 399 s)
- Protocol: character-level precision/recall, retrieved spans union-merged per file before
  scoring (equivalent to the official formula for non-overlapping retrievers; prevents
  double-counting from our overlapping windows). See `backend/eval/scoring.py`.
- Reproduce: `cd backend && .venv/Scripts/python -m eval.run_eval --data-dir
  ../benchmark_data/lbr --benchmarks contractnli cuad maud privacy_qa --ks 1,2,4,8,16,32,64`

## Recall@k — ours (hybrid, local) vs published best (hosted, naive-500)

| dataset     | k=1 ours / theirs | k=8 ours / theirs | k=64 ours / theirs |
|-------------|-------------------|-------------------|--------------------|
| contractnli | **27.0** / 11.3   | **50.8** / 45.6   | 84.8 / **86.6**    |
| cuad        | 5.8 / **12.6**    | **48.8** / 40.7   | **79.3** / 75.7    |
| maud        | **2.7** / 2.5     | **11.9** / 8.8    | **28.2** / 25.6    |
| privacy_qa  | **22.1** / 7.5    | **73.4** / 32.4   | **95.4** / 66.1    |
| OVERALL     | **14.4** / 8.5    | **46.2** / 31.9   | **71.9** / 63.5    |

(theirs = arXiv:2408.10343 Table 4; overall = equal-weight mean of the four datasets,
their published "ALL" row appears garbled in the HTML rendering)

## Full ours table (recall / precision)

| dataset     | k=1      | k=2      | k=4      | k=8      | k=16     | k=32     | k=64     |
|-------------|----------|----------|----------|----------|----------|----------|----------|
| contractnli | 27.0/6.0 | 35.4/3.9 | 42.5/2.4 | 50.8/1.5 | 63.0/0.9 | 74.3/0.5 | 84.8/0.3 |
| cuad        | 5.8/1.5  | 21.9/3.3 | 38.6/2.8 | 48.8/2.0 | 62.3/1.2 | 70.9/0.6 | 79.3/0.4 |
| maud        | 2.7/1.1  | 3.2/0.7  | 7.4/1.1  | 11.9/0.9 | 15.5/0.5 | 22.5/0.4 | 28.2/0.3 |
| privacy_qa  | 22.1/6.0 | 39.4/6.3 | 53.8/4.8 | 73.4/4.0 | 88.7/2.7 | 92.0/1.4 | 95.4/0.8 |
| OVERALL     | 14.4/3.6 | 25.0/3.6 | 35.6/2.8 | 46.2/2.1 | 57.4/1.3 | 64.9/0.8 | 71.9/0.4 |

## Notes for the paper

- Precision is not directly comparable across chunk sizes (their chunks ~500 chars, ours
  ~2,800); recall@matched-k is the primary comparison, precision needs a chunk-size sweep
  (M2 ablation) before it can be tabled against theirs.
- Weak spots to investigate in error analysis: cuad@1 (5.8 vs 12.6), contractnli@64
  (84.8 vs 86.6), and the cuad precision anomaly rising from k=1 (1.5) to k=2 (3.3) —
  suggests the top fused hit is sometimes a large, weakly-relevant chunk (pre-heading or
  merged-tiny chunk candidates).
- MAUD is hard for everyone (merger agreements, huge documents; both systems < 30% @64).
- Their Cohere rerank rows *hurt* (domain mismatch) — encouraging for the rerank-free
  local story; the defined-term graph (M2) targets exactly the cuad/contractnli gaps.
