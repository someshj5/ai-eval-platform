from typing import Iterable


def chunk_records(
    records: Iterable[dict],
    chunk_size: int,
):
    chunk = []

    for record in records:
        chunk.append(record)

        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk