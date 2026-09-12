import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Treina um adapter LoRA com mlx-lm em Apple Silicon."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Repositorio Hugging Face MLX ou caminho local do modelo convertido.",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Diretorio com train.jsonl e valid.jsonl/validation.jsonl.",
    )
    parser.add_argument(
        "--adapter-path",
        default="adapters/llama3_2_3b_pubmedqa",
        help="Diretorio onde o adapter LoRA sera salvo.",
    )
    parser.add_argument("--iters", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--num-layers", type=int, default=8)
    parser.add_argument("--grad-accumulation-steps", type=int, default=8)
    parser.add_argument(
        "--no-mask-prompt",
        action="store_false",
        dest="mask_prompt",
        help="Calcula loss tambem no prompt. Por padrao, treina apenas na resposta.",
    )
    parser.add_argument(
        "--grad-checkpoint",
        action="store_true",
        help="Reduz uso de memoria recomputando ativacoes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o comando sem executar o treino.",
    )
    parser.set_defaults(mask_prompt=True)
    return parser.parse_args()


def ensure_dataset_files(data_dir: Path) -> None:
    train_path = data_dir / "train.jsonl"
    valid_path = data_dir / "valid.jsonl"
    validation_path = data_dir / "validation.jsonl"

    if not train_path.exists():
        raise FileNotFoundError(
            f"Nao encontrei {train_path}. Execute primeiro: python3 1_preparar_dataset.py"
        )

    if not valid_path.exists():
        if validation_path.exists():
            shutil.copyfile(validation_path, valid_path)
            print(f"Arquivo {valid_path} criado a partir de {validation_path}.")
        else:
            print(
                f"Aviso: {valid_path} nao existe. O treino seguira sem validacao.",
                file=sys.stderr,
            )


def build_command(args: argparse.Namespace) -> list[str]:
    command = [
        "mlx_lm.lora",
        "--model",
        args.model,
        "--train",
        "--data",
        args.data_dir,
        "--adapter-path",
        args.adapter_path,
        "--iters",
        str(args.iters),
        "--batch-size",
        str(args.batch_size),
        "--learning-rate",
        str(args.learning_rate),
        "--num-layers",
        str(args.num_layers),
        "--grad-accumulation-steps",
        str(args.grad_accumulation_steps),
    ]

    if args.mask_prompt:
        command.append("--mask-prompt")

    if args.grad_checkpoint:
        command.append("--grad-checkpoint")

    return command


def ensure_mlx_lm_is_available() -> None:
    if shutil.which("mlx_lm.lora"):
        return

    raise RuntimeError(
        "Nao encontrei o comando 'mlx_lm.lora' no ambiente Python ativo.\n\n"
        "No Mac M1, execute:\n"
        "  cd /caminho/do/projeto/trabalho3/fine-tuning\n"
        "  source .venv/bin/activate\n"
        "  pip install -U \"mlx-lm[train]\"\n\n"
        "Depois valide com:\n"
        "  which mlx_lm.lora\n"
        "  mlx_lm.lora --help"
    )


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)

    ensure_dataset_files(data_dir)

    command = build_command(args)
    print("Comando de treino:")
    print(" ".join(command))

    if args.dry_run:
        return

    ensure_mlx_lm_is_available()
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
