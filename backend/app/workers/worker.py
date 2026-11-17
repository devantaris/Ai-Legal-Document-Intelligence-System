"""Sovereign Ingestion Worker Daemon.

Runs in an isolated process/container, polling the Redis queue for contract
ingestion, OCR extraction, defined-term indexing, and dense vectorization.

Start via:
    python -m app.workers.worker
"""

import json
import logging
import signal
import sys
import time
import uuid

from app.core.config import settings
from app.services.ingestion import run_ingestion
from app.workers.queue import INGESTION_QUEUE_KEY, get_redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SovereignWorker] %(message)s",
)
logger = logging.getLogger(__name__)

_STOP_REQUESTED = False


def _signal_handler(signum, frame):
    global _STOP_REQUESTED
    logger.info("Termination signal received (%s). Draining active job and shutting down...", signum)
    _STOP_REQUESTED = True


def start_worker():
    global _STOP_REQUESTED
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    client = get_redis_client()
    if client is None:
        logger.error("Cannot connect to Redis at %s. Exiting worker.", settings.REDIS_URL)
        sys.exit(1)

    logger.info("Sovereign LegalIQ Ingestion Worker started.")
    logger.info("Connected to Redis: %s", settings.REDIS_URL)
    logger.info("Queue key: %s", INGESTION_QUEUE_KEY)
    logger.info("Active LLM Provider: %s", settings.LLM_PROVIDER)
    logger.info("Waiting for contract ingestion tasks...")

    while not _STOP_REQUESTED:
        try:
            # Block for up to 2 seconds waiting for task
            item = client.blpop(INGESTION_QUEUE_KEY, timeout=2)
            if item is None:
                continue

            _, raw_payload = item
            task_data = json.loads(raw_payload)
            doc_id_str = task_data.get("document_id")
            if not doc_id_str:
                continue

            doc_id = uuid.UUID(doc_id_str)
            logger.info("--> Processing contract ingestion for doc_id: %s", doc_id)
            start_t = time.time()
            run_ingestion(doc_id)
            duration = time.time() - start_t
            logger.info("<-- Finished ingestion for doc_id %s in %.2fs", doc_id, duration)

        except Exception as exc:
            logger.error("Worker exception during job execution: %s", exc, exc_info=True)
            time.sleep(1)

    logger.info("Sovereign Worker exited cleanly.")


if __name__ == "__main__":
    start_worker()
