import asyncio
import time

from evaluator.checkpoint import CheckpointStore
from evaluator.chunker import chunk_records
from evaluator.evaluator import evaluate_record
from evaluator.reader import read_jsonl
from evaluator.rate_limiter import AsyncRateLimiter


MAX_CONCURRENCY = 5
CHUNK_SIZE = 3
MAX_REQUESTS = 5
RATE_LIMIT_PERIOD = 1.0


async def evaluate_with_limit(record, semaphore, checkpoint, request_id,rate_limiter):
    record_id = record["id"]

    status = checkpoint.get_status(request_id, record_id)

    if status == "completed":
        print(f"SKIP  {record_id} (already completed)")
        return None

    async with semaphore:
        print(f"CONCURRENCY SLOT {record_id}")

        await rate_limiter.acquire()

        print(f"RATE LIMIT SLOT {record_id}")

        checkpoint.mark_processing(
            request_id,
            record_id,
        )



        try:
            result = await evaluate_record(record)

            checkpoint.mark_completed(
                request_id,
                record_id,
                result["score"],
                result["reason"],
            )

            print(f"DONE {record_id}")

            return result

        except Exception as exc:
            checkpoint.mark_failed(
                request_id,
                record_id,
                str(exc),
            )

            print(f"FAILED {record_id}: {exc}")

            raise


async def process_chunk(chunk, request_id, checkpoint):
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    rate_limiter = AsyncRateLimiter(
        max_requests=MAX_REQUESTS,
        period=RATE_LIMIT_PERIOD,
    )

    tasks = [
        evaluate_with_limit(
            record,
            semaphore,
            checkpoint,
            request_id,
            rate_limiter,
        )
        for record in chunk
    ]

    return await asyncio.gather(*tasks)

async def run():
    records = list(
        read_jsonl("data/dataset.jsonl")
    )

    chunks = chunk_records(
        records,
        CHUNK_SIZE,
    )

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENCY
    )

    checkpoint = CheckpointStore()

    for chunk in chunks:
        await process_chunk(
            chunk,
            semaphore,
            checkpoint,
        )

    checkpoint.close()


if __name__ == "__main__":
    asyncio.run(run())