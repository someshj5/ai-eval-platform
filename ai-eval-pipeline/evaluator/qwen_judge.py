# evaluator/qwen_judge.py

import json

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


class QwenJudge:
    def __init__(self, model_name: str = MODEL_NAME):
        self.device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        print(f"Loading Qwen model on {self.device}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
        )

        self.model.to(self.device)
        self.model.eval()

        print("Qwen model loaded.")

    def judge(self, record: dict) -> dict:
        """
        Evaluate one dataset record using Qwen.
        """

        prompt = self._build_prompt(record)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI evaluation judge. "
                    "Evaluate the answer against the expected answer. "
                    "Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=False,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

        response = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        return self._parse_response(response)

    def _build_prompt(self, record: dict) -> str:
        return f"""
Evaluate the following answer.

Question:
{record["question"]}

Expected answer:
{record["expected"]}

Actual answer:
{record["answer"]}

Determine whether the actual answer is correct.

Return exactly this JSON structure:

{{
    "score": 1,
    "reason": "brief explanation"
}}

Use:
- score = 1 if the answer is correct
- score = 0 if the answer is incorrect
""".strip()

    def _parse_response(self, response: str) -> dict:
        """
        Convert Qwen's JSON response into a Python dictionary.
        """

        try:
            result = json.loads(response)

            return {
                "score": int(result["score"]),
                "reason": result["reason"],
            }

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return {
                "score": 0,
                "reason": f"Invalid judge response: {response}",
            }