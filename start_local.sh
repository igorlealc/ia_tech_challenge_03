#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
VENV_DIR="$ROOT_DIR/.venv"

mkdir -p "$LOG_DIR"

ASSISTANT_PID=""

cleanup() {
  kill "$ASSISTANT_PID" 2>/dev/null
  cd "$ROOT_DIR"
  docker compose down
}

wait_for_http() {
  url="$1"
  name="$2"

  for _ in $(seq 1 90); do
    if curl "$url" >/dev/null 2>&1; then
      echo "$name iniciado"
      return
    fi
    sleep 1
  done

  echo "Nao foi possivel iniciar $name"
  exit 1
}

prepare_python_env() {
  cd "$ROOT_DIR"

  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
  fi

  source "$VENV_DIR/bin/activate"
  python -m pip install -r "$ROOT_DIR/requirements.txt"
}

trap cleanup EXIT

cd "$ROOT_DIR"
docker compose up --build -d
wait_for_http "http://localhost:8000/health" "ML"
wait_for_http "http://localhost:8080" "Frontend"

prepare_python_env
cd "$ROOT_DIR/assistant"
export ML_API_URL="http://localhost:8000"
export LLM_PROVIDER="mlx"
export MLX_WORKDIR="../fine-tuning"
export MLX_GENERATE_BIN="../.venv/bin/mlx_lm.generate"
export MLX_MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit"
export MLX_ADAPTER_PATH="adapters/llama3_2_3b_pubmedqa"
export EXTRACT_FEATURES_WITH_LLM="true"
export FEATURE_EXTRACTION_MLX_GENERATE_BIN="../.venv/bin/mlx_lm.generate"
export FEATURE_EXTRACTION_MLX_MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit"
export TRANSLATE_TO_PTBR="true"
export TRANSLATION_MLX_GENERATE_BIN="../.venv/bin/mlx_lm.generate"
export TRANSLATION_MLX_MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit"
python run_local.py > "$LOG_DIR/assistant.log" 2>&1 &
ASSISTANT_PID="$!"
deactivate
wait_for_http "http://localhost:8010/health" "Assistant"

open "http://localhost:8080"

echo "Aplicacao iniciada"
echo "Frontend: http://localhost:8080"
echo "Assistant: http://localhost:8010"
echo "ML: http://localhost:8000"
echo "Logs: $LOG_DIR"
echo "Pressione Ctrl+C para encerrar"

wait "$ASSISTANT_PID"
