from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from hindsight_client import Hindsight

from app.config import settings

CASE_CODE_PATTERN = re.compile(r"\bLOT-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")


@dataclass
class MemoryHit:
    text: str
    memory_type: str
    case_codes: list[str]


class HindsightService:
    def __init__(self) -> None:
        if not settings.hindsight_api_key:
            raise RuntimeError("HINDSIGHT_API_KEY is not configured")
        self.client = Hindsight(
            base_url=settings.hindsight_base_url,
            api_key=settings.hindsight_api_key,
            timeout=60.0,
        )
        self.bank_id = settings.hindsight_bank_id

    async def close(self) -> None:
        await self.client.aclose()

    async def recall(self, query: str) -> list[MemoryHit]:
        result = await self.client.arecall(
            bank_id=self.bank_id,
            query=query,
            budget="low",
        )
        hits: list[MemoryHit] = []
        for item in result.results:
            text = str(getattr(item, "text", "") or "")
            hits.append(
                MemoryHit(
                    text=text,
                    memory_type=str(getattr(item, "type", "memory") or "memory"),
                    case_codes=sorted(set(CASE_CODE_PATTERN.findall(text))),
                )
            )
        return hits

    async def reflect(self, query: str) -> str:
        response = await self.client.areflect(
            bank_id=self.bank_id,
            query=query,
            budget="low",
        )
        return str(getattr(response, "text", "") or "")

    async def retain_verified_outcome(
        self,
        *,
        case_code: str,
        content: str,
        verification_id: str,
    ) -> None:
        await self.client.aretain(
            bank_id=self.bank_id,
            content=content,
            context=(
                "LotLens verified manufacturing investigation outcome. "
                "This memory is derived from a QA verification record."
            ),
            metadata={
                "project": "lotlens",
                "case_code": case_code,
                "verification_id": verification_id,
                "record_type": "qa_verified_outcome",
            },
            operation_id=f"lotlens-verification-{verification_id}",
        )
