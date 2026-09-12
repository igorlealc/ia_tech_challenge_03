from __future__ import annotations

import os
from pathlib import Path


class Settings:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        fine_tuning_dir = project_root / "fine-tuning"

        self.ml_api_url = os.getenv("ML_API_URL", "http://localhost:8000").rstrip("/")
        self.llm_provider = os.getenv("LLM_PROVIDER", "mlx").lower()
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm_model = os.getenv("LLM_MODEL", "pubmedqa-llama")
        self.mlx_generate_bin = os.getenv("MLX_GENERATE_BIN", "mlx_lm.generate")
        self.mlx_model = os.getenv(
            "MLX_MODEL",
            "mlx-community/Llama-3.2-3B-Instruct-4bit",
        )
        self.mlx_adapter_path = os.getenv(
            "MLX_ADAPTER_PATH",
            "adapters/llama3_2_3b_pubmedqa",
        )
        self.mlx_workdir = Path(os.getenv("MLX_WORKDIR", str(fine_tuning_dir)))
        self.mlx_max_tokens = int(os.getenv("MLX_MAX_TOKENS", "512"))
        self.mlx_timeout_seconds = int(os.getenv("MLX_TIMEOUT_SECONDS", "180"))
        self.extract_features_with_llm = (
            os.getenv("EXTRACT_FEATURES_WITH_LLM", "true").lower() == "true"
        )
        self.feature_extraction_mlx_generate_bin = os.getenv(
            "FEATURE_EXTRACTION_MLX_GENERATE_BIN",
            self.mlx_generate_bin,
        )
        self.feature_extraction_mlx_model = os.getenv(
            "FEATURE_EXTRACTION_MLX_MODEL",
            self.mlx_model,
        )
        self.feature_extraction_mlx_adapter_path = os.getenv(
            "FEATURE_EXTRACTION_MLX_ADAPTER_PATH",
            "",
        )
        self.feature_extraction_mlx_workdir = Path(
            os.getenv("FEATURE_EXTRACTION_MLX_WORKDIR", str(self.mlx_workdir))
        )
        self.feature_extraction_mlx_max_tokens = int(
            os.getenv("FEATURE_EXTRACTION_MLX_MAX_TOKENS", "384")
        )
        self.feature_extraction_mlx_timeout_seconds = int(
            os.getenv("FEATURE_EXTRACTION_MLX_TIMEOUT_SECONDS", "120")
        )
        self.translate_to_ptbr = (
            os.getenv("TRANSLATE_TO_PTBR", "false").lower() == "true"
        )
        self.translation_mlx_generate_bin = os.getenv(
            "TRANSLATION_MLX_GENERATE_BIN",
            self.mlx_generate_bin,
        )
        self.translation_mlx_model = os.getenv("TRANSLATION_MLX_MODEL", self.mlx_model)
        self.translation_mlx_adapter_path = os.getenv(
            "TRANSLATION_MLX_ADAPTER_PATH",
            "",
        )
        self.translation_mlx_workdir = Path(
            os.getenv("TRANSLATION_MLX_WORKDIR", str(self.mlx_workdir))
        )
        self.translation_mlx_max_tokens = int(
            os.getenv("TRANSLATION_MLX_MAX_TOKENS", str(self.mlx_max_tokens))
        )
        self.translation_mlx_timeout_seconds = int(
            os.getenv(
                "TRANSLATION_MLX_TIMEOUT_SECONDS",
                str(self.mlx_timeout_seconds),
            )
        )
        self.audit_log_path = Path(
            os.getenv(
                "AUDIT_LOG_PATH",
                Path(__file__).resolve().parents[1] / "logs" / "audit.jsonl",
            )
        )


settings = Settings()
