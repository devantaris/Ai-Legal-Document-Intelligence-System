"""Evaluation harness for the journal paper (docs/paper-plan.md).

M1: retrieval evaluation over LegalBench-RAG (Pipitone & Alami, 2024,
arXiv:2408.10343). The package is standalone: it reuses the app's services but
runs against an isolated `legal_ai_eval` database and forces the local Ollama
embedding stack, so dev data and dev config are never touched.
"""
