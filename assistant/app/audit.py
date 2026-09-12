from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.config import settings


def write_audit_log(
    *,
    user_message: str,
    should_use_predictive_model: bool | None,
    predictive_decision_reason: str | None,
    predictive_decision_error: str | None,
    clinical_payload: dict[str, Any] | None,
    features: dict[str, Any] | None,
    feature_extraction_error: str | None,
    sources: list[str],
    tool_called: str | None,
    tool_result: dict[str, Any] | None,
    llm_provider: str,
    llm_error: str | None,
    translation_enabled: bool,
    translation_error: str | None,
    safety_notice_applied: bool,
) -> str:
    settings.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    session_id = f"demo-local-{uuid4().hex[:8]}"
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "session_id": session_id,
        "message_received": bool(user_message.strip()),
        "should_use_predictive_model": should_use_predictive_model,
        "predictive_decision_reason": predictive_decision_reason,
        "predictive_decision_error": predictive_decision_error,
        "clinical_payload": clinical_payload,
        "features": features,
        "feature_extraction_error": feature_extraction_error,
        "tool_called": tool_called,
        "tool_result": tool_result,
        "llm_provider": llm_provider,
        "llm_error": llm_error,
        "translation_enabled": translation_enabled,
        "translation_error": translation_error,
        "sources": sources,
        "safety_notice_applied": safety_notice_applied,
    }
    with settings.audit_log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=True) + "\n")
    return session_id
