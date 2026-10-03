"""Background task entry points (re-exported for clarity)."""

from app.services.ingestion import run_ingestion

__all__ = ["run_ingestion"]
