from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    tokens_used: int | None = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
