from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


class InvalidFeatureSchemaError(ValueError):
    def __init__(self, missing: list[str], unexpected: list[str]) -> None:
        self.missing = missing
        self.unexpected = unexpected
        super().__init__("Payload com schema de features invalido.")


class ModelService:
    def __init__(
        self,
        model_path: Path,
        model_name: str = "RandomForestClassifier",
        model_version: str = "0.1.0",
    ) -> None:
        self.model_path = model_path
        self.model_name = model_name
        self.model_version = model_version
        self.model: Any | None = None
        self.feature_names: list[str] = []
        self.positive_class = 1

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Modelo nao encontrado em {self.model_path}")

        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.feature_names = list(bundle["feature_names"])
        self.positive_class = int(bundle.get("positive_class", 1))

    def metadata(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "positive_class": self.positive_class,
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "loaded": self.is_loaded,
        }

    def predict(self, payload: Any) -> dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Modelo ainda nao foi carregado.")

        rows = self._normalize_payload(payload)
        dataframe = self._build_dataframe(rows)
        predictions = self.model.predict(dataframe)
        probabilities = self.model.predict_proba(dataframe)[:, self.positive_class]

        return {
            "predictions": [
                {
                    "prediction": int(prediction),
                    "probability": float(probability),
                    "positive_class": self.positive_class,
                    "model_name": self.model_name,
                    "model_version": self.model_version,
                }
                for prediction, probability in zip(predictions, probabilities)
            ]
        }

    def _normalize_payload(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and "features" in payload:
            features = payload["features"]
            if isinstance(features, list):
                return features
            if isinstance(features, dict):
                return [features]

        if isinstance(payload, list):
            return payload

        raise ValueError(
            "Payload esperado: {'features': {...}}, {'features': [{...}]} ou lista de features."
        )

    def _build_dataframe(self, rows: list[dict[str, Any]]) -> pd.DataFrame:
        for row in rows:
            self._validate_row(row)
        return pd.DataFrame([{name: row[name] for name in self.feature_names} for row in rows])

    def _validate_row(self, row: dict[str, Any]) -> None:
        provided = set(row)
        expected = set(self.feature_names)
        missing = sorted(expected - provided)
        unexpected = sorted(provided - expected)

        if missing or unexpected:
            raise InvalidFeatureSchemaError(missing=missing, unexpected=unexpected)
