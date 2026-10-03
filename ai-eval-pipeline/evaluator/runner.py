import asyncio

from evaluator.checkpoint import CheckpointStore
from evaluator.chunker import chunk_records
from evaluator.evaluator import evaluate_record
from evaluator.reader import read_jsonl


MAX_CONCURRENCY = 5
CHUNK_SIZE = 3
REQUEST_ID = "req_001"

async def evaluate_with_limit(
    record: dict,
    semaphore: asyncio.Semaphore,
    checkpoint: CheckpointStore,
):
    record_id = record["id"]

    status = checkpoint.get_status(
        REQUEST_ID,
        record_id,
    )

    # Completed records are never evaluated again.
    if status == "completed":
        print(
            f"SKIP  {record_id} "
            f"(already completed)"
        )
        return None

    async with semaphore:
        print(f"START {record_id}")

        checkpoint.mark_processing(
            REQUEST_ID,
            record_id,
        )

        try:
            result = await evaluate_record(record)

            checkpoint.mark_completed(
                REQUEST_ID,
                record_id,
                result["score"],
                result["reason"],
            )

            print(f"DONE  {record_id}")

            return result

        except Exception as exc:
            checkpoint.mark_failed(
                REQUEST_ID,
                record_id,
                str(exc),
            )

            print(
                f"FAILED {record_id}: {exc}"
            )

            raise

# async def evaluate_with_limit(
#     record: dict,
#     semaphore: asyncio.Semaphore,
#     checkpoint: CheckpointStore,
# ):
#     record_id = record["id"]

#     if checkpoint.is_completed(
#         REQUEST_ID,
#         record_id,
#     ):
#         print(f"SKIP  {record_id} (already completed)")
#         return None

#     async with semaphore:
#         print(f"START {record_id}")

#         result = await evaluate_record(record)

#         checkpoint.save_result(
#             REQUEST_ID,
#             record_id,
#             result,
#         )

#         print(f"DONE  {record_id}")

#         return result


async def process_chunk(
    chunk: list[dict],
    semaphore: asyncio.Semaphore,
    checkpoint: CheckpointStore,
):
    print(
        f"\nPROCESSING CHUNK: "
        f"{[record['id'] for record in chunk]}"
    )

    tasks = [
        evaluate_with_limit(
            record,
            semaphore,
            checkpoint,
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