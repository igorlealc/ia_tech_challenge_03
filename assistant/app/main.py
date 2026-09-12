from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.audit import write_audit_log
from app.config import settings
from app.graph import graph
from app.safety import SAFETY_NOTICE
from app.schemas import ChatMessage, ChatRequest, ChatResponse


app = FastAPI(
    title="Medical Assistant API",
    version="0.1.0",
    description="Assistente medico academico local com LangGraph e Random Forest.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "ml_api_url": settings.ml_api_url,
        "llm_provider": settings.llm_provider,
        "ollama_base_url": settings.ollama_base_url,
        "llm_model": settings.llm_model,
        "mlx_model": settings.mlx_model,
        "mlx_adapter_path": settings.mlx_adapter_path,
        "mlx_workdir": str(settings.mlx_workdir),
        "extract_features_with_llm": settings.extract_features_with_llm,
        "feature_extraction_mlx_model": settings.feature_extraction_mlx_model,
        "feature_extraction_mlx_adapter_path": (
            settings.feature_extraction_mlx_adapter_path
        ),
        "translate_to_ptbr": settings.translate_to_ptbr,
        "translation_mlx_model": settings.translation_mlx_model,
        "translation_mlx_adapter_path": settings.translation_mlx_adapter_path,
        "audit_log_path": str(settings.audit_log_path),
    }


@app.post("/chat/messages", response_model=ChatResponse)
def chat_messages(request: ChatRequest) -> ChatResponse:
    result = graph.invoke({"user_message": request.message})
    sources = list(dict.fromkeys(result.get("sources") or []))

    write_audit_log(
        user_message=request.message,
        should_use_predictive_model=result.get("should_use_predictive_model"),
        predictive_decision_reason=result.get("predictive_decision_reason"),
        predictive_decision_error=result.get("predictive_decision_error"),
        clinical_payload=result.get("clinical_payload"),
        features=result.get("features"),
        feature_extraction_error=result.get("feature_extraction_error"),
        sources=sources,
        tool_called=result.get("tool_called"),
        tool_result=result.get("tool_result"),
        llm_provider=settings.llm_provider,
        llm_error=result.get("llm_error"),
        translation_enabled=settings.translate_to_ptbr,
        translation_error=result.get("translation_error"),
        safety_notice_applied=SAFETY_NOTICE in result["answer"],
    )

    return ChatResponse(
        message=ChatMessage(
            role="assistant",
            content=result["answer"],
        ),
        sources=sources,
        safety_notice=SAFETY_NOTICE,
    )
