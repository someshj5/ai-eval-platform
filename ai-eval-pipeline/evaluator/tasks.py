import asyncio

from evaluator.celery_app import celery_app


@celery_app.task(name="evaluator.process_chunk")
def process_chunk_task(chunk: list[dict]):
    print(
        f"WORKER RECEIVED CHUNK: "
        f"{[record['id'] for record in chunk]}"
    )

    # For now, just prove that Celery
    # received the chunk.
    return {
        "status": "received",
        "record_ids": [
            record["id"]
            for record in chunk
        ],
    }