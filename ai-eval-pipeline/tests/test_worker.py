from evaluator.tasks import process_chunk_task


REQUEST_ID = "req_001"

chunk = [
    {"id": "1", "question": "What is 2 + 2?", "answer": "4", "expected": "4"},
    {"id": "2", "question": "What is the capital of France?", "answer": "Paris", "expected": "Paris"},
    {"id": "3", "question": "What is 10 / 2?", "answer": "6", "expected": "5"},
]

result = process_chunk_task.delay(
    REQUEST_ID,
    chunk,
)

print("Task ID:", result.id)