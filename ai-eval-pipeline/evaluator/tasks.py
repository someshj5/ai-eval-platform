import asyncio

from evaluator.celery_app import celery_app
from evaluator.checkpoint import CheckpointStore
from evaluator.runner import process_chunk


@celery_app.task(name="evaluator.process_chunk")
def process_chunk_task(request_id: str, chunk: list[dict]):
    print(
        f"WORKER RECEIVED CHUNK: "
        f"request_id={request_id}, "
        f"records={[record['id'] for record in chunk]}"
    )

    checkpoint = CheckpointStore()

    try:
        results = asyncio.run(
            process_chunk(
                chunk=chunk,
                request_id=request_id,
                checkpoint=checkpoint,
            )
        )

        return {
            "status": "completed",
            "request_id": request_id,
            "record_ids": [
                record["id"]
                for record in chunk
            ],
            "results": results,
        }

    finally:
        checkpoint.close()