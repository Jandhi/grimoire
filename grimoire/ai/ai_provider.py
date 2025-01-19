from enum import StrEnum
from typing import TypeVar, Type, Any, Optional
from openai import OpenAI
from pydantic import BaseModel

from grimoire.core.logger import Logger


class Model(StrEnum):
    gpt4o = "gpt-4o"
    gpt4o_mini = "gpt-4o-mini"


def load_key() -> str:
    with open("..\\..\\key.txt", "r") as f:
        return f.read().strip()


class AIProvider:
    def __init__(
        self, api_key: str = None, model: str = Model.gpt4o_mini, logger: Logger = None
    ):
        api_key = api_key or load_key()
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.logger = logger or Logger()

    # Format type should be a class that inherits from pydantic.BaseModel
    # The output can be None if the response is invalid
    def generate(self, context: str, prompt: str, format_type: Type) -> Optional[Any]:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": context,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format=format_type,
        )

        output = completion.choices[0].message.parsed

        if not format_type.model_validate(output):
            self.logger.error("Invalid response format")
            return None

        return output
