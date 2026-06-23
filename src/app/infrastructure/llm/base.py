from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
