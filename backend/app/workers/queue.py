import json
import logging
import time
import uuid
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

INGESTION_QUEUE_KEY = "legaliq:ingestion_queue"
PROGRESS_KEY_PREFIX = "legaliq:doc_progress:"
PROGRESS_CHANNEL_PREFIX = "legaliq:doc_channel:"

_redis_pool: redis.ConnectionPool | None = None


def get_redis_client() -> redis.Redis | None:
    """Return a shared Redis client, or None if Redis is unreachable."""
    global _redis_pool
    if not settings.REDIS_URL:
        return None

    try:
        if _redis_pool is None:
            _redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                decode_responses=True,
            )
        client = redis.Redis(connection_pool=_redis_pool)
        client.ping()
        return client
    except Exception as exc:
        logger.warning("Redis is unavailable (%s). Falling back to synchronous thread execution.", exc)
        return None


def enqueue_ingestion_task(document_id: uuid.UUID) -> bool:
    """Enqueue an ingestion task into Redis for sovereign worker nodes.

    Returns True if successfully pushed to Redis, False if fallback needed.
    """
    client = get_redis_client()
    if client is None:
        return False

    payload = json.dumps(
        {
            "task": "ingestion",
            "document_id": str(document_id),
            "enqueued_at": time.time(),
        }
    )
    try:
        client.rpush(INGESTION_QUEUE_KEY, payload)
        publish_task_progress(
            document_id=document_id,
            status="queued",
            step="Queued in sovereign worker pipeline",
            progress_pct=5,
        )
        return True
    except Exception as exc:
        logger.warning("Failed to enqueue ingestion task to Redis: %s", exc)
        return False


def publish_task_progress(
    document_id: uuid.UUID,
    status: str,
    step: str,
    progress_pct: int,
) -> None:
    """Publish real-time document processing stage and progress percentage."""
    client = get_redis_client()
    data = {
        "document_id": str(document_id),
        "status": status,
        "step": step,
        "progress_pct": max(0, min(100, progress_pct)),
        "updated_at": time.time(),
    }
    raw = json.dumps(data)

    if client is not None:
        try:
            # 1. Store in progress cache key (expires in 2 hours)
            client.set(f"{PROGRESS_KEY_PREFIX}{document_id}", raw, ex=7200)
            # 2. Publish to live pub/sub channel for streaming SSE listeners
            client.publish(f"{PROGRESS_CHANNEL_PREFIX}{document_id}", raw)
        except Exception:
            pass


def get_task_progress(document_id: uuid.UUID) -> dict[str, Any] | None:
    """Fetch the latest real-time progress update for a document."""
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(f"{PROGRESS_KEY_PREFIX}{document_id}")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None
