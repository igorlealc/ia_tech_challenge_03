from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from app.model_service import InvalidFeatureSchemaError, ModelService


MODEL_PATH = Path(
    os.getenv(
        "MODEL_PATH",
        Path(__file__).resolve().parents[1] / "model" / "random_forest.joblib",
    )
)

model_service = ModelService(model_path=MODEL_PATH)

app = FastAPI(
    title="SISCAN Random Forest API",
    version="0.1.0",
    description="API academica para inferencia do modelo Random Forest treinado com dados SISCAN.",
)


@app.on_event("startup")
def load_model() -> None:
    model_service.load()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_loaded": model_service.is_loaded,
        "model_name": model_service.model_name,
        "model_version": model_service.model_version,
    }


@app.get("/metadata")
def metadata() -> dict[str, Any]:
    return model_service.metadata()


@app.post("/predict")
async def predict(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
        return model_service.predict(payload)
    except InvalidFeatureSchemaError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_FEATURE_SCHEMA",
                "missing": exc.missing,
                "unexpected": exc.unexpected,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PAYLOAD",
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PREDICTION_ERROR",
                "message": str(exc),
            },
        ) from exc
