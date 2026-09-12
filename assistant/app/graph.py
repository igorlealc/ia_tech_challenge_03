from __future__ import annotations

import re
import subprocess
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from app.config import settings
from app.safety import SYSTEM_PROMPT, apply_safety_footer
from app.tools import (
    clinical_data_to_features,
    extract_clinical_json_from_text,
    extract_features_from_text,
    prever_risco_cancer_mama,
)


class AssistantState(TypedDict, total=False):
    user_message: str
    should_use_predictive_model: bool
    predictive_decision_reason: str | None
    predictive_decision_error: str | None
    clinical_payload: dict[str, Any] | None
    features: dict[str, Any] | None
    tool_result: dict[str, Any] | None
    answer: str
    sources: list[str]
    tool_called: str | None
    feature_extraction_error: str | None
    llm_error: str | None
    translation_error: str | None


def _decide_predictive_model(state: AssistantState) -> AssistantState:
    should_use = False
    reason = None
    error = None
    forced = _should_force_predictive_model(state["user_message"])

    if forced:
        should_use = True
        reason = "usuario_solicitou_modelo_preditivo_ou_caso_mamario_detectado"
    else:
        try:
            decision = _invoke_predictive_decision_mlx(state["user_message"])
            should_use = bool(decision.get("usar_modelo_preditivo"))
            reason = str(decision.get("motivo") or "")
        except Exception as exc:
            error = str(exc)
            features = extract_features_from_text(state["user_message"])
            should_use = features is not None
            reason = "fallback_heuristico_detectou_features" if should_use else None

    return {
        **state,
        "should_use_predictive_model": should_use,
        "predictive_decision_reason": reason,
        "predictive_decision_error": error,
        "sources": [],
        "tool_called": None,
    }


def _should_force_predictive_model(user_message: str) -> bool:
    normalized = user_message.lower()
    explicit_terms = [
        "consulte o modelo preditivo",
        "modelo preditivo",
        "random forest",
        "randomforest",
        "prever risco",
        "predicao",
        "predição",
    ]
    mammography_terms = [
        "mamografia",
        "mamografico",
        "mamográfico",
        "rastreamento",
        "cancer de mama",
        "câncer de mama",
        "nodulo",
        "nódulo",
        "secrecao papilar",
        "secreção papilar",
    ]
    has_age = re.search(r"\b\d{2,3}\s*anos?\b", normalized) is not None
    return any(term in normalized for term in explicit_terms) or (
        has_age and any(term in normalized for term in mammography_terms)
    )


def _should_extract_features(state: AssistantState) -> str:
    if state.get("should_use_predictive_model"):
        return "extract_features"
    return "answer"


def _extract_features(state: AssistantState) -> AssistantState:
    clinical_payload = None
    feature_extraction_error = None
    features = None

    direct_payload = extract_clinical_json_from_text(state["user_message"])
    if direct_payload is not None:
        clinical_payload = direct_payload
        features = clinical_data_to_features(direct_payload)

    if features is None and settings.extract_features_with_llm:
        try:
            clinical_payload = _invoke_feature_extraction_mlx(state["user_message"])
            features = clinical_data_to_features(clinical_payload)
        except Exception as exc:
            feature_extraction_error = str(exc)

    if features is None:
        features = extract_features_from_text(state["user_message"])

    return {
        **state,
        "clinical_payload": clinical_payload,
        "features": features,
        "feature_extraction_error": feature_extraction_error,
    }


def _should_call_risk_tool(state: AssistantState) -> str:
    if state.get("features"):
        return "risk_tool"
    return "answer"


def _call_risk_tool(state: AssistantState) -> AssistantState:
    try:
        result = prever_risco_cancer_mama.invoke({"features": state["features"]})
    except Exception as exc:
        result = {"error": str(exc)}
    return {
        **state,
        "tool_result": result,
        "tool_called": "prever_risco_cancer_mama",
        "sources": ["RandomForestClassifier"],
    }


def _build_context(state: AssistantState) -> str:
    context = state["user_message"]
    if state.get("clinical_payload"):
        context += (
            "\n\nJSON clinico interno extraido pela IA intermediaria "
            "(nao exibir ao usuario):\n"
            f"{state['clinical_payload']}"
        )
    if state.get("features"):
        context += (
            "\n\nFeatures tecnicas internas enviadas ao modelo preditivo "
            "(nao exibir ao usuario):\n"
            f"{state['features']}"
        )
    if state.get("tool_result"):
        context += (
            "\n\nResultado da ferramenta RandomForestClassifier:\n"
            f"{state['tool_result']}"
        )
    return context


def _build_mlx_prompt(state: AssistantState) -> str:
    system_prompt = (
        f"{SYSTEM_PROMPT}\n"
        "Responda exclusivamente em portugues do Brasil.\n"
        "Nao responda em ingles, espanhol ou outro idioma.\n"
        "Se o usuario escrever em outro idioma, ainda assim responda em portugues do Brasil."
    )
    user_prompt = (
        "Mensagem do usuario e contexto disponivel:\n"
        f"{_build_context(state)}\n\n"
        "Gere a resposta final ao usuario. Nao copie nem exponha o JSON clinico, "
        "as features tecnicas ou o payload enviado ao modelo preditivo. "
        "Se houver resultado do RandomForestClassifier, interprete classe, "
        "probabilidade e limitacoes em linguagem clinica academica. "
        "Explique as fontes usadas e responda exclusivamente em portugues do Brasil."
    )
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def _build_translation_prompt(answer: str) -> str:
    system_prompt = (
        "Voce e um tradutor medico-academico. Sua tarefa e converter o texto "
        "recebido para portugues do Brasil, mantendo significado, cautelas "
        "clinicas, fontes citadas, numeros, siglas e estrutura. Nao acrescente "
        "novas informacoes. Nao remova avisos de seguranca."
    )
    user_prompt = (
        "Traduza o texto abaixo exclusivamente para portugues do Brasil. "
        "Se o texto ja estiver em portugues do Brasil, apenas revise para manter "
        "clareza e naturalidade, sem alterar o conteudo.\n\n"
        f"{answer}"
    )
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def _build_feature_extraction_prompt(user_message: str) -> str:
    system_prompt = (
        "Voce e um extrator de dados clinicos para um sistema academico. "
        "Leia o texto do medico e retorne somente um objeto JSON valido. "
        "Nao escreva explicacoes, markdown ou comentarios. "
        "Nao invente informacoes ausentes; use null quando nao estiver claro."
    )
    user_prompt = (
        "Extraia os campos abaixo do caso clinico. Responda somente JSON com "
        "estas chaves: idade, sexo, raca_cor, risco_elevado, historico_familiar, "
        "mamografia_previa, tempo_mamografia_anterior_meses, "
        "exame_mamas_profissional, indicacao.\n\n"
        "Regras:\n"
        "- idade: numero inteiro em anos ou null.\n"
        "- sexo: feminino, masculino, ignorado ou null.\n"
        "- raca_cor: branca, preta, parda, amarela, indigena ou null.\n"
        "- risco_elevado, historico_familiar, mamografia_previa e "
        "exame_mamas_profissional: true, false ou null.\n"
        "- tempo_mamografia_anterior_meses: numero inteiro em anos ou null.\n"
        "- indicacao: rastreamento, diagnostica/investigacao ou null.\n\n"
        "Texto do medico:\n"
        f"{user_message}"
    )
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def _build_predictive_decision_prompt(user_message: str) -> str:
    system_prompt = (
        f"{SYSTEM_PROMPT}\n"
        "Voce e a IA principal com fine-tuning. Antes de responder ao usuario, "
        "decida se o caso deve consultar o modelo preditivo academico "
        "RandomForestClassifier de cancer de mama. Responda somente JSON valido, "
        "sem markdown e sem explicacoes fora do JSON."
    )
    user_prompt = (
        "Analise a mensagem do medico e decida se ha um caso de triagem, "
        "rastreamento ou investigacao mamaria com dados clinicos suficientes para "
        "tentar consulta ao modelo preditivo.\n\n"
        "Retorne exatamente este formato:\n"
        "{\"usar_modelo_preditivo\": true|false, \"motivo\": \"texto curto\"}\n\n"
        "Use true quando houver idade e contexto mamario, rastreamento, mamografia, "
        "nodulo, sintoma mamario ou avaliacao de risco. Use false para perguntas "
        "conceituais, conversas gerais ou quando nao houver caso clinico.\n\n"
        "Mensagem do medico:\n"
        f"{user_message}"
    )
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt}"
        "<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
_SEPARATOR_PATTERN = re.compile(r"(?m)^\s*=+\s*$")
_METRIC_LINE_PATTERN = re.compile(
    r"^\s*(Prompt|Generation):\s+\d+(\.\d+)?\s+tokens?\b|^\s*Peak memory:",
    re.IGNORECASE,
)
_BARE_TOKEN_METRIC_PATTERN = re.compile(
    r"^\s*\d+(\.\d+)?\s+tokens?,\s+\d+(\.\d+)?\s+tokens-per-sec\b",
    re.IGNORECASE,
)
_SPECIAL_TOKEN_PATTERN = re.compile(r"<\|[^|]+?\|>")


def _strip_prompt_echo(text: str, prompt: str) -> str:
    if prompt in text:
        return text.split(prompt, maxsplit=1)[-1].strip()

    if text.startswith("Prompt:"):
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip().endswith("?") or line.strip().endswith("."):
                return "\n".join(lines[index + 1 :]).strip()

    return text.strip()


def _remove_mlx_metrics(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if _METRIC_LINE_PATTERN.search(line) or _BARE_TOKEN_METRIC_PATTERN.search(line):
            continue
        lines.append(line)
    return _SPECIAL_TOKEN_PATTERN.sub("", "\n".join(lines)).strip()


def _looks_like_metrics(text: str) -> bool:
    cleaned = text.strip()
    if not cleaned:
        return True
    return bool(_METRIC_LINE_PATTERN.search(cleaned)) and not any(
        not (
            _METRIC_LINE_PATTERN.search(line)
            or _BARE_TOKEN_METRIC_PATTERN.search(line)
        )
        for line in cleaned.splitlines()
        if line.strip()
    )


def _extract_mlx_answer(stdout: str, prompt: str) -> str:
    text = stdout.strip()
    if not text:
        return ""

    text = _ANSI_ESCAPE_PATTERN.sub("", text)

    blocks = [
        block.strip()
        for block in _SEPARATOR_PATTERN.split(text)
        if block.strip()
    ]
    candidates = []
    for block in blocks:
        block = _strip_prompt_echo(block, prompt)
        block = _remove_mlx_metrics(block)
        if block and not _looks_like_metrics(block):
            candidates.append(block)

    if candidates:
        return max(candidates, key=len).strip()

    marker = "Generation:"
    if marker not in text:
        return _remove_mlx_metrics(_strip_prompt_echo(text, prompt))

    generated = text.split(marker, maxsplit=1)[-1].strip()
    if "==========" in generated:
        generated = generated.split("==========", maxsplit=1)[0].strip()
    return _remove_mlx_metrics(generated)


def _invoke_feature_extraction_mlx(user_message: str) -> dict[str, Any]:
    prompt = _build_feature_extraction_prompt(user_message)
    command = [
        settings.feature_extraction_mlx_generate_bin,
        "--model",
        settings.feature_extraction_mlx_model,
        "--prompt",
        prompt,
        "--max-tokens",
        str(settings.feature_extraction_mlx_max_tokens),
    ]

    if settings.feature_extraction_mlx_adapter_path:
        command.extend(["--adapter-path", settings.feature_extraction_mlx_adapter_path])

    result = subprocess.run(
        command,
        cwd=settings.feature_extraction_mlx_workdir,
        capture_output=True,
        check=True,
        text=True,
        timeout=settings.feature_extraction_mlx_timeout_seconds,
    )

    extracted = _extract_mlx_answer(result.stdout, prompt)
    payload = extract_clinical_json_from_text(extracted)
    if payload is None:
        raise RuntimeError(
            "Extrator MLX nao retornou um objeto JSON clinico valido."
        )
    return payload


def _invoke_predictive_decision_mlx(user_message: str) -> dict[str, Any]:
    prompt = _build_predictive_decision_prompt(user_message)
    command = [
        settings.mlx_generate_bin,
        "--model",
        settings.mlx_model,
        "--adapter-path",
        settings.mlx_adapter_path,
        "--prompt",
        prompt,
        "--max-tokens",
        "160",
    ]

    result = subprocess.run(
        command,
        cwd=settings.mlx_workdir,
        capture_output=True,
        check=True,
        text=True,
        timeout=settings.mlx_timeout_seconds,
    )

    decision_text = _extract_mlx_answer(result.stdout, prompt)
    payload = extract_clinical_json_from_text(decision_text)
    if payload is None:
        raise RuntimeError("IA principal nao retornou JSON de decisao valido.")
    return payload


def _invoke_mlx(state: AssistantState) -> str:
    prompt = _build_mlx_prompt(state)
    command = [
        settings.mlx_generate_bin,
        "--model",
        settings.mlx_model,
        "--adapter-path",
        settings.mlx_adapter_path,
        "--prompt",
        prompt,
        "--max-tokens",
        str(settings.mlx_max_tokens),
    ]

    result = subprocess.run(
        command,
        cwd=settings.mlx_workdir,
        capture_output=True,
        check=True,
        text=True,
        timeout=settings.mlx_timeout_seconds,
    )

    answer = _extract_mlx_answer(result.stdout, prompt)
    if not answer:
        raise RuntimeError("mlx_lm.generate nao retornou texto em stdout.")
    return answer


def _invoke_translation_mlx(answer: str) -> str:
    prompt = _build_translation_prompt(answer)
    command = [
        settings.translation_mlx_generate_bin,
        "--model",
        settings.translation_mlx_model,
        "--prompt",
        prompt,
        "--max-tokens",
        str(settings.translation_mlx_max_tokens),
    ]

    if settings.translation_mlx_adapter_path:
        command.extend(["--adapter-path", settings.translation_mlx_adapter_path])

    result = subprocess.run(
        command,
        cwd=settings.translation_mlx_workdir,
        capture_output=True,
        check=True,
        text=True,
        timeout=settings.translation_mlx_timeout_seconds,
    )

    translated = _extract_mlx_answer(result.stdout, prompt)
    if not translated:
        raise RuntimeError("Tradutor MLX nao retornou texto em stdout.")
    return translated


def _invoke_ollama(state: AssistantState) -> str:
    llm = ChatOllama(
        model=settings.llm_model,
        base_url=settings.ollama_base_url,
        temperature=0,
    )
    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=_build_context(state)),
        ]
    )
    return str(response.content)


def _fallback_answer(state: AssistantState) -> str:
    sources = state.get("sources") or []
    if state.get("tool_result"):
        if "error" in state["tool_result"]:
            return (
                "Recebi features estruturadas, mas nao consegui consultar a "
                "ferramenta RandomForestClassifier. Confirme se a API local "
                "`trabalho3/ml` esta rodando em `http://localhost:8000` antes "
                "de usar o resultado preditivo no video.\n\n"
                f"Fontes: {', '.join(sources)}."
            )

        prediction = state["tool_result"]["predictions"][0]
        return (
            "Analise academica local: a ferramenta preditiva RandomForestClassifier "
            f"retornou classe {prediction['prediction']} com probabilidade "
            f"{prediction['probability']:.4f} para a classe positiva "
            f"{prediction['positive_class']}. Use esse resultado apenas como apoio "
            "a triagem e correlacione com historia clinica, exame fisico, exames "
            "complementares e validacao da equipe responsavel.\n\n"
            f"Fontes: {', '.join(sources)}."
        )

    return (
        "Posso apoiar a triagem academica organizando os dados do caso, "
        "indicando informacoes faltantes e acionando o modelo "
        "RandomForestClassifier quando o texto trouxer dados suficientes. "
        "Informe em linguagem natural, quando disponivel: idade, sexo, raca/cor, "
        "se ha risco elevado ou historico familiar, se ja fez mamografia, tempo "
        "desde a ultima mamografia, se houve exame das mamas por profissional e "
        "se a indicacao e rastreamento ou investigacao de sintoma. "
        "A resposta deve ser validada por profissional habilitado.\n\n"
        "Fontes: regras de seguranca do assistente."
    )


def _predictive_result_summary(state: AssistantState) -> str | None:
    tool_result = state.get("tool_result")
    if not tool_result or "error" in tool_result:
        return None

    predictions = tool_result.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        return None

    prediction = predictions[0]
    predicted_class = prediction.get("prediction")
    probability = prediction.get("probability")
    positive_class = prediction.get("positive_class")
    model_name = prediction.get("model_name", "RandomForestClassifier")
    model_version = prediction.get("model_version")

    probability_text = (
        f"{float(probability):.4f}"
        if isinstance(probability, int | float)
        else str(probability)
    )
    version_text = f" versao {model_version}" if model_version else ""

    return (
        f"Resultado do modelo preditivo: o {model_name}{version_text} retornou "
        f"classe {predicted_class} com probabilidade {probability_text} para a "
        f"classe positiva {positive_class}. Esse valor deve ser interpretado "
        "apenas como apoio academico a triagem, sem valor diagnostico isolado."
    )


def _mentions_predictive_result(answer: str) -> bool:
    normalized = answer.lower()
    has_model = (
        "randomforest" in normalized
        or "random forest" in normalized
        or "modelo preditivo" in normalized
        or "ferramenta preditiva" in normalized
    )
    has_result = (
        "probabilidade" in normalized
        or "classe" in normalized
        or "predicao" in normalized
        or "predição" in normalized
    )
    return has_model and has_result


def _ensure_predictive_result_interpreted(
    answer: str,
    state: AssistantState,
) -> str:
    summary = _predictive_result_summary(state)
    if summary is None or _mentions_predictive_result(answer):
        return answer
    return f"{summary}\n\n{answer.strip()}"


def _looks_like_internal_payload_answer(answer: str) -> bool:
    text = answer.strip()
    technical_markers = [
        "CO_IDADE_PACIENTE_NUM",
        "CO_TEMPO_MAMO_ANTERIOR_NUM",
        "SG_SEXO_",
        "TP_RESP_",
        "CO_IND_CLINICA_",
        "TP_MAMOGRAFIA_",
        "clinical_payload",
        '"features"',
        "'features'",
    ]
    if text.startswith("{") and any(marker in text for marker in technical_markers):
        return True
    return any(marker in text for marker in technical_markers)


def _answer(state: AssistantState) -> AssistantState:
    sources = list(state.get("sources") or [])
    translation_error = None

    try:
        if settings.llm_provider == "mlx":
            answer = _invoke_mlx(state)
            if state.get("tool_result") and _looks_like_internal_payload_answer(answer):
                answer = _fallback_answer({**state, "sources": sources})
            answer = _ensure_predictive_result_interpreted(answer, state)
            sources.append("LLM fine-tuned via MLX")
        else:
            answer = _invoke_ollama(state)
            answer = _ensure_predictive_result_interpreted(answer, state)
            sources.append("LLM via Ollama")
        llm_error = None
    except Exception as exc:
        answer = _fallback_answer({**state, "sources": sources})
        llm_error = str(exc)

    if settings.translate_to_ptbr:
        try:
            answer = _invoke_translation_mlx(answer)
        except Exception as exc:
            translation_error = str(exc)

    answer = _ensure_predictive_result_interpreted(answer, state)

    return {
        **state,
        "answer": apply_safety_footer(answer),
        "sources": sources or ["regras de seguranca do assistente"],
        "llm_error": llm_error,
        "translation_error": translation_error,
    }


def create_graph():
    builder = StateGraph(AssistantState)
    builder.add_node("decide_predictive_model", _decide_predictive_model)
    builder.add_node("extract_features", _extract_features)
    builder.add_node("risk_tool", _call_risk_tool)
    builder.add_node("answer", _answer)
    builder.set_entry_point("decide_predictive_model")
    builder.add_conditional_edges(
        "decide_predictive_model",
        _should_extract_features,
        {
            "extract_features": "extract_features",
            "answer": "answer",
        },
    )
    builder.add_conditional_edges(
        "extract_features",
        _should_call_risk_tool,
        {
            "risk_tool": "risk_tool",
            "answer": "answer",
        },
    )
    builder.add_edge("risk_tool", "answer")
    builder.add_edge("answer", END)
    return builder.compile()


graph = create_graph()
