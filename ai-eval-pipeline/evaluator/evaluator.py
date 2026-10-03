from evaluator.nvidia_judge import NvidiaJudge


judge = NvidiaJudge()


# async def evaluate_record(record: dict) -> dict:

#     result = await judge.evaluate(record)

#     return {
#         "record_id": record["id"],
#         "score": result["score"],
#         "reason": result["reason"],
#         "status": "completed",
#     }



async def evaluate_record(record: dict) -> dict:
    result = await judge.evaluate(record)

    return {
        "record_id": record["id"],
        "score": result["score"],
        "reason": result["reason"],
        "status": "completed",
    }