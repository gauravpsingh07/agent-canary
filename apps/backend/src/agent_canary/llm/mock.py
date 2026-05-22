import json
import re
from typing import Any

from agent_canary.llm.base import JsonObject, JsonSchema


class MockLLMProvider:
    def __init__(self, model_name: str = "mock-agent-canary-v1") -> None:
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        structured = self.generate_structured(
            prompt=prompt,
            system_prompt=system_prompt,
            schema={},
            temperature=temperature,
        )
        return json.dumps(structured, sort_keys=True)[:max_tokens]

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str | None,
        schema: JsonSchema,
        temperature: float = 0.0,
    ) -> JsonObject:
        del system_prompt, schema, temperature
        normalized_prompt = prompt.lower()

        if (
            "retrieved evidence:" in normalized_prompt
            and ("use the 2023" in normalized_prompt or "2023 policy note" in normalized_prompt)
        ):
            citation = self._first_retrieved_citation(prompt)
            return self._agent_output(
                reasoning_summary=(
                    "The retrieved evidence appears stale for a current-policy answer."
                ),
                action_type="answer",
                answer=(
                    "The retrieved policy context appears stale, so I cannot give a "
                    "definitive current answer."
                ),
                risk_level="medium",
                requires_approval=False,
                confidence=0.7,
                citations=[citation] if citation else [],
            )

        if "retrieved evidence:" in normalized_prompt and "current refund" in normalized_prompt:
            citation = self._first_retrieved_citation(prompt)
            if (
                "without citations" in normalized_prompt
                or "do not include citations" in normalized_prompt
            ):
                citation = None
            return self._agent_output(
                reasoning_summary="The answer is grounded in retrieved refund policy evidence.",
                action_type="answer",
                answer=(
                    "Current refund policy allows standard refund review, while high-value "
                    "refunds require human approval."
                ),
                risk_level="low",
                requires_approval=False,
                confidence=0.84,
                citations=[citation] if citation else [],
            )

        if "guarantee refunds" in normalized_prompt or "unsupported claim" in normalized_prompt:
            return self._agent_output(
                reasoning_summary=(
                    "The available evidence is insufficient for a guaranteed refund claim."
                ),
                action_type="refusal",
                answer="I need stronger supporting evidence before making that claim.",
                risk_level="medium",
                requires_approval=False,
                confidence=0.82,
            )

        if "enterprise refund exception" in normalized_prompt:
            return self._agent_output(
                reasoning_summary=(
                    "The retrieved evidence does not support the enterprise exception policy."
                ),
                action_type="refusal",
                answer="I need stronger retrieved evidence before answering this policy question.",
                risk_level="medium",
                requires_approval=False,
                confidence=0.78,
            )

        if self._contains_any(normalized_prompt, ("system prompt", "api_key", "api key", "secret")):
            return self._agent_output(
                reasoning_summary="The request attempts to reveal hidden instructions or secrets.",
                action_type="refusal",
                answer="I cannot reveal system prompts, credentials, or secrets.",
                risk_level="critical",
                requires_approval=False,
                confidence=0.98,
            )

        if "delete" in normalized_prompt and "user" in normalized_prompt:
            return self._agent_output(
                reasoning_summary="Deleting a user is destructive and must be reviewed.",
                action_type="request_human_review",
                answer=None,
                tool_call={
                    "tool_name": "delete_user",
                    "arguments": {
                        "user_id": "user_12345",
                        "reason": "User deletion requires human review.",
                    },
                },
                risk_level="critical",
                requires_approval=True,
                confidence=0.94,
            )

        if "refund" in normalized_prompt:
            amount = 500 if "$500" in normalized_prompt or "500" in normalized_prompt else 25
            return self._agent_output(
                reasoning_summary="Refunds above the automatic limit require human approval.",
                action_type="request_human_review" if amount > 25 else "tool_call",
                answer=None,
                tool_call={
                    "tool_name": "refund_payment",
                    "arguments": {
                        "payment_id": "pay_123",
                        "amount": amount,
                        "reason": "Customer refund request.",
                    },
                },
                risk_level="high" if amount > 25 else "medium",
                requires_approval=amount > 25,
                confidence=0.9,
            )

        if "support ticket" in normalized_prompt or "create a ticket" in normalized_prompt:
            return self._agent_output(
                reasoning_summary="Creating an internal support ticket is a low-risk action.",
                action_type="tool_call",
                answer=None,
                tool_call={
                    "tool_name": "create_ticket",
                    "arguments": {
                        "title": "Customer callback",
                        "description": "User requested a callback.",
                        "priority": "low",
                    },
                },
                risk_level="low",
                requires_approval=False,
                confidence=0.87,
            )

        if self._contains_any(normalized_prompt, ("weak", "stale", "unsupported", "citation")):
            return self._agent_output(
                reasoning_summary="The available evidence is insufficient for a grounded answer.",
                action_type="refusal",
                answer="I need stronger supporting evidence before answering.",
                risk_level="medium",
                requires_approval=False,
                confidence=0.82,
            )

        return self._agent_output(
            reasoning_summary="The prompt can be answered without proposing a risky tool call.",
            action_type="answer",
            answer="This mock response is deterministic for tests and demos.",
            risk_level="low",
            requires_approval=False,
            confidence=0.8,
        )

    @staticmethod
    def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
        return any(needle in text for needle in needles)

    @staticmethod
    def _first_retrieved_citation(prompt: str) -> dict[str, str] | None:
        chunk_match = re.search(r"'chunk_id': '([^']+)'|\"chunk_id\": \"([^\"]+)\"", prompt)
        document_match = re.search(
            r"'document_id': '([^']+)'|\"document_id\": \"([^\"]+)\"",
            prompt,
        )
        chunk_id = first_match_group(chunk_match)
        document_id = first_match_group(document_match)
        if not chunk_id and not document_id:
            return None
        return {
            "document_id": document_id or "",
            "chunk_id": chunk_id or "",
            "quote": "Retrieved refund policy evidence.",
        }

    @staticmethod
    def _agent_output(
        *,
        reasoning_summary: str,
        action_type: str,
        answer: str | None,
        risk_level: str,
        requires_approval: bool,
        confidence: float,
        tool_call: dict[str, Any] | None = None,
        citations: list[dict[str, str]] | None = None,
    ) -> JsonObject:
        return {
            "reasoning_summary": reasoning_summary,
            "action_type": action_type,
            "answer": answer,
            "tool_call": tool_call,
            "risk_level": risk_level,
            "requires_approval": requires_approval,
            "confidence": confidence,
            "citations": citations or [],
        }


def first_match_group(match: re.Match[str] | None) -> str | None:
    if match is None:
        return None
    return next((group for group in match.groups() if group), None)
