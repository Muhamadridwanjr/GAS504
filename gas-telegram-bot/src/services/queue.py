"""
GAS Bot — Redis Job Queue
Redis keys:
  q:high           LIST  — Signal jobs      (LPUSH enqueue, BRPOP dequeue)
  q:medium         LIST  — Analysis jobs
  q:low            LIST  — Analyst + Scanner jobs
  q:feed           LIST  — Feed jobs
  job:{id}         STRING JSON — Job data, TTL 5 min
"""
import json
import time
import uuid
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Optional

from src.services.redis_client import get_redis

_JOB_TTL = 300  # 5 minutes


class JobType(str, Enum):
    SIGNAL   = "signal"
    ANALYSIS = "analysis"
    ANALYST  = "analyst"
    SCANNER  = "scanner"
    FEED     = "feed"


class JobStatus(str, Enum):
    QUEUED     = "queued"
    PROCESSING = "processing"
    DONE       = "done"
    FAILED     = "failed"


_PRIORITY_QUEUE = {
    JobType.SIGNAL:   "q:high",
    JobType.ANALYSIS: "q:medium",
    JobType.ANALYST:  "q:low",
    JobType.SCANNER:  "q:low",
    JobType.FEED:     "q:feed",
}

_ETA_SECONDS = {
    "q:high":  "3-5",
    "q:medium": "5-10",
    "q:low":  "10-20",
}


@dataclass
class Job:
    id:          str
    type:        JobType
    status:      JobStatus
    gas_user_id: str
    tg_user_id:  int
    chat_id:     int
    message_id:  int          # Telegram message to edit with result
    pair:        str = ""
    style:       str = ""
    pairs:       list = field(default_factory=list)
    plan:        str = "free"
    ai_tier:     str = "basic"   # basic | advanced | pro | ultra
    cache_ttl:   int = 30        # 0 = no cache
    created_at:  float = field(default_factory=time.time)
    started_at:  float = 0.0
    finished_at: float = 0.0
    error:       str = ""
    retry:       int = 0


def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


async def enqueue(
    job_type:    JobType,
    gas_user_id: str,
    tg_user_id:  int,
    chat_id:     int,
    message_id:  int,
    pair:        str = "",
    style:       str = "",
    pairs:       list = None,
    plan:        str = "free",
    ai_tier:     str = "basic",
    cache_ttl:   int = 30,
) -> str:
    """Push a job to the appropriate priority queue. Returns job_id."""
    r = await get_redis()
    job_id = uuid.uuid4().hex[:12]
    job = Job(
        id=job_id,
        type=job_type,
        status=JobStatus.QUEUED,
        gas_user_id=gas_user_id,
        tg_user_id=tg_user_id,
        chat_id=chat_id,
        message_id=message_id,
        pair=pair,
        style=style,
        pairs=pairs or [],
        plan=plan,
        ai_tier=ai_tier,
        cache_ttl=cache_ttl,
    )
    data = asdict(job)
    queue = _PRIORITY_QUEUE[job_type]
    pipe = r.pipeline()
    pipe.set(_job_key(job_id), json.dumps(data), ex=_JOB_TTL)
    pipe.lpush(queue, job_id)
    await pipe.execute()
    return job_id


async def get_job(job_id: str) -> Optional[Job]:
    r = await get_redis()
    raw = await r.get(_job_key(job_id))
    if not raw:
        return None
    data = json.loads(raw)
    data["type"]   = JobType(data["type"])
    data["status"] = JobStatus(data["status"])
    return Job(**data)


async def update_job(job_id: str, **fields) -> None:
    r = await get_redis()
    raw = await r.get(_job_key(job_id))
    if not raw:
        return
    data = json.loads(raw)
    data.update({k: (v.value if isinstance(v, Enum) else v) for k, v in fields.items()})
    await r.set(_job_key(job_id), json.dumps(data), ex=_JOB_TTL)


async def dequeue(queues: list[str], timeout: int = 5) -> Optional[Job]:
    """BRPOP from multiple queues (priority order). Returns Job or None on timeout."""
    r = await get_redis()
    result = await r.brpop(queues, timeout=timeout)
    if not result:
        return None
    _, job_id = result
    return await get_job(job_id)


def eta_text(job_type: JobType) -> str:
    queue = _PRIORITY_QUEUE.get(job_type, "q:medium")
    return _ETA_SECONDS.get(queue, "5-10")
