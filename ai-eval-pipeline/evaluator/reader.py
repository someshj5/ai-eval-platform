import json
from pathlib import Path


def read_jsonl(path: str):
    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            yield json.loads(line)