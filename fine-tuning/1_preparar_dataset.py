import json
import random
from pathlib import Path

INPUT = Path("data/ori_pqal.json")
TRAIN_OUTPUT = Path("data/train.jsonl")
VALIDATION_OUTPUT = Path("data/validation.jsonl")

random.seed(42)


def build_prompt(item: dict) -> str:
    contexts = "\n\n".join(item.get("CONTEXTS", []))
    question = item.get("QUESTION", "")

    return (
        "Voce e um assistente especializado em responder perguntas biomedicas "
        "com base exclusivamente no contexto fornecido.\n\n"
        f"Contexto:\n{contexts}\n\n"
        f"Pergunta:\n{question}\n\n"
        "Responda com uma das opcoes: yes, no ou maybe. "
        "Depois, forneca uma justificativa curta baseada no contexto."
    )


def build_answer(item: dict) -> str:
    decision = item.get("final_decision", "").strip()
    long_answer = item.get("LONG_ANSWER", "").strip()
    return f"{decision}\n\n{long_answer}".strip()


def to_message(item: dict) -> dict:
    return {
        "messages": [
            {"role": "user", "content": build_prompt(item)},
            {"role": "assistant", "content": build_answer(item)},
        ]
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [to_message(item) for item in data.values()]
    random.shuffle(rows)

    split_index = int(len(rows) * 0.9)
    train_rows = rows[:split_index]
    validation_rows = rows[split_index:]

    write_jsonl(TRAIN_OUTPUT, train_rows)
    write_jsonl(VALIDATION_OUTPUT, validation_rows)

    print(f"Treino: {len(train_rows)} exemplos")
    print(f"Validacao: {len(validation_rows)} exemplos")


if __name__ == "__main__":
    main()