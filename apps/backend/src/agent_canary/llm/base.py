from collections.abc import Mapping
from typing import Any, Protocol

JsonObject = dict[str, Any]
JsonSchema = Mapping[str, Any]


class LLMProvider(Protocol):
    @property
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        ...

    @property
    def model_name(self) -> str:
        """Provider model identifier used for generation."""
        ...

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        """Generate plain text from a prompt."""
        ...

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str | None,
        schema: JsonSchema,
        temperature: float = 0.0,
    ) -> JsonObject:
        """Generate a JSON object matching the caller's requested schema."""
        ...
