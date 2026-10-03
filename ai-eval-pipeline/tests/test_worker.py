from evaluator.tasks import process_chunk_task

chunk = [
    {"id": "1"},
    {"id": "2"},
    {"id": "3"},
]

result = process_chunk_task.delay(chunk)

print("Task ID:", result.id)