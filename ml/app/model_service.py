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
        self.target_column = "TARGET_CANCER_MAMA_PROVAVEL"
        self.metrics: dict[str, Any] = {}

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
        self.target_column = str(bundle.get("target_column", self.target_column))
        self.metrics = dict(bundle.get("metrics") or {})

    def metadata(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "target_column": self.target_column,
            "positive_class": self.positive_class,
            "class_labels": self._class_labels(),
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "metrics": self.metrics,
            "loaded": self.is_loaded,
        }

    def predict(self, payload: Any) -> dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Modelo ainda nao foi carregado.")

        rows = self._normalize_payload(payload)
        dataframe = self._build_dataframe(rows)
        predictions = self.model.predict(dataframe)
        prediction_probabilities = self.model.predict_proba(dataframe)
        positive_class_index = self._positive_class_index()
        positive_probabilities = prediction_probabilities[:, positive_class_index]
        class_labels = self._class_labels()

        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "target_column": self.target_column,
            "positive_class": self.positive_class,
            "probability_meaning": (
                "Probabilidade estimada pelo classificador para a classe positiva "
                "do alvo TARGET_CANCER_MAMA_PROVAVEL. Nao representa acuracia, "
                "precisao do modelo ou probabilidade clinica diagnostica."
            ),
            "model_metrics": self.metrics,
            "predictions": [
                {
                    "prediction": int(prediction),
                    "positive_class_probability": float(positive_probability),
                    "predicted_class_probability": float(
                        prediction_probabilities[row_index][
                            class_labels.index(int(prediction))
                        ]
                    ),
                    "probability": float(positive_probability),
                    "positive_class": self.positive_class,
                    "model_name": self.model_name,
                    "model_version": self.model_version,
                }
                for row_index, (prediction, positive_probability) in enumerate(
                    zip(predictions, positive_probabilities)
                )
            ]
        }

    def _class_labels(self) -> list[int]:
        if self.model is None:
            return []
        return [int(label) for label in self.model.classes_]

    def _positive_class_index(self) -> int:
        class_labels = self._class_labels()
        if self.positive_class not in class_labels:
            raise RuntimeError(
                f"Classe positiva {self.positive_class} nao encontrada em {class_labels}."
            )
        return class_labels.index(self.positive_class)

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
