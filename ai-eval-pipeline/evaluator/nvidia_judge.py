


import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()


class NvidiaJudge:
    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ):
        api_key = os.getenv("NVIDIA_API_KEY_OAI")

        if not api_key:
            raise RuntimeError(
                "NVIDIA_API_KEY is not set"
            )

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )

        self.model = model

    async def evaluate(self, record: dict) -> dict:

        prompt = self._build_prompt(record)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI evaluation judge. "
                        "Evaluate the actual answer against "
                        "the expected answer. "
                        "Return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            max_tokens=150,
        )

        content = response.choices[0].message.content

        return self._parse_response(content)

    def _build_prompt(self, record: dict) -> str:

        return f"""
Evaluate this answer.

Question:
{record["question"]}

Expected answer:
{record["expected"]}

Actual answer:
{record["answer"]}

Return exactly:

{{
    "score": 1,
    "reason": "brief explanation"
}}

Rules:

- score must be 1 when the actual answer is correct.
- score must be 0 when the actual answer is incorrect.
- reason must briefly explain the decision.
""".strip()

    def _parse_response(self, content: str) -> dict:

        try:
            result = json.loads(content)

            return {
                "score": int(result["score"]),
                "reason": result["reason"],
            }

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid judge response: {content}"
            ) from exc