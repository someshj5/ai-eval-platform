from evaluator.chunker import chunk_records


def test_chunk_records():
    records = [
        {"id": "1"},
        {"id": "2"},
        {"id": "3"},
        {"id": "4"},
        {"id": "5"},
        {"id": "6"},
        {"id": "7"},
    ]

    chunks = list(
        chunk_records(records, chunk_size=3)
    )

    assert chunks == [
        [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ],
        [
            {"id": "4"},
            {"id": "5"},
            {"id": "6"},
        ],
        [
            {"id": "7"},
        ],
    ]