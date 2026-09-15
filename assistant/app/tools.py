from __future__ import annotations

import json
import re
from typing import Any

import httpx
from langchain_core.tools import tool

from app.config import settings


FEATURE_NAMES = [
    "CO_TEMPO_MAMO_ANTERIOR_NUM",
    "CO_IDADE_PACIENTE_NUM",
    "SG_SEXO_F",
    "SG_SEXO_I",
    "SG_SEXO_M",
    "CO_RACA_COR_01",
    "CO_RACA_COR_02",
    "CO_RACA_COR_03",
    "CO_RACA_COR_04",
    "CO_RACA_COR_05",
    "TP_RESP_APRES_RISC_ELEV_CANCER_01",
    "TP_RESP_APRES_RISC_ELEV_CANCER_02",
    "TP_RESP_APRES_RISC_ELEV_CANCER_03",
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01",
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02",
    "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03",
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01",
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02",
    "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03",
    "CO_IND_CLINICA_01",
    "CO_IND_CLINICA_02",
    "TP_MAMOGRAFIA_RASTREAMENT_01",
    "TP_MAMOGRAFIA_RASTREAMENT_02",
    "TP_MAMOGRAFIA_RASTREAMENT_03",
]


def _normalized(text: str) -> str:
    replacements = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüç",
        "aaaaaeeeeiiiiooooouuuuc",
    )
    return text.lower().translate(replacements)


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = _normalized(str(value)).strip()
    if normalized in {"sim", "s", "true", "1", "yes", "y"}:
        return True
    if normalized in {"nao", "n", "false", "0", "no"}:
        return False
    return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    match = re.search(r"\d+", str(value))
    if match:
        return int(match.group(0))
    return None


def _mammogram_time_code_from_months(months: int | None) -> int:
    if months is None:
        return 0
    if months < 12:
        return 1
    if months <= 24:
        return 2
    if months <= 36:
        return 3
    return 4


def _mammogram_time_code_from_value(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int) and 0 <= value <= 5:
        return value
    normalized = _normalized(str(value))
    if "nunca" in normalized:
        return 5
    if "mais de 3" in normalized or "maior que 3" in normalized:
        return 4
    if "ano" in normalized:
        years = _to_int(value)
        if years is None:
            return 0
        if years == 1:
            return 2
        if years == 2:
            return 2
        if years == 3:
            return 3
        return 4
    months = _to_int(value)
    return _mammogram_time_code_from_months(months)


def _one_hot(features: dict[str, Any], selected: str, options: list[str]) -> None:
    for option in options:
        features[option] = 1 if option == selected else 0


def _extract_age(text: str) -> int | None:
    patterns = [
        r"\b(?:idade|paciente|mulher|homem|feminina|masculino)\D{0,20}(\d{2,3})\s*anos?\b",
        r"\b(\d{2,3})\s*anos?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            age = int(match.group(1))
            if 10 <= age <= 120:
                return age
    return None


def _extract_previous_mammogram_time(text: str) -> int:
    if "nunca fez mamografia" in text or "sem mamografia previa" in text:
        return 5

    month_match = re.search(r"(?:mamografia|mamo)[^.]{0,50}?ha\s+(\d+)\s+mes", text)
    if month_match:
        return _mammogram_time_code_from_months(int(month_match.group(1)))

    year_match = re.search(r"(?:mamografia|mamo)[^.]{0,50}?ha\s+(\d+)\s+ano", text)
    if year_match:
        years = int(year_match.group(1))
        if years == 1:
            return 2
        if years == 2:
            return 2
        if years == 3:
            return 3
        return 4

    return 0


def _detect_sex(text: str) -> str:
    if any(term in text for term in ["masculino", "homem", "sexo m"]):
        return "SG_SEXO_M"
    if any(term in text for term in ["feminino", "mulher", "paciente feminina", "paciente ficticia", "sexo f"]):
        return "SG_SEXO_F"
    return "SG_SEXO_I"


def _detect_race(text: str) -> str | None:
    mapping = {
        "branca": "CO_RACA_COR_01",
        "branco": "CO_RACA_COR_01",
        "preta": "CO_RACA_COR_02",
        "preto": "CO_RACA_COR_02",
        "negra": "CO_RACA_COR_02",
        "negro": "CO_RACA_COR_02",
        "parda": "CO_RACA_COR_03",
        "pardo": "CO_RACA_COR_03",
        "amarela": "CO_RACA_COR_04",
        "amarelo": "CO_RACA_COR_04",
        "indigena": "CO_RACA_COR_05",
    }
    for term, feature in mapping.items():
        if term in text:
            return feature
    return None


def _detect_yes_no_unknown(
    text: str,
    *,
    yes_terms: list[str],
    no_terms: list[str],
    yes_feature: str,
    no_feature: str,
    unknown_feature: str,
) -> str:
    if any(term in text for term in no_terms):
        return no_feature
    if any(term in text for term in yes_terms):
        return yes_feature
    return unknown_feature


def _has_affirmed_term(text: str, terms: list[str]) -> bool:
    for term in terms:
        if term not in text:
            continue
        negated_pattern = rf"\b(?:sem|nega|ausencia de|ausente)\b[^.]{{0,30}}\b{re.escape(term)}\b"
        if re.search(negated_pattern, text):
            continue
        return True
    return False


def _extract_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        candidate = text[match.start() :]
        try:
            parsed, _ = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _is_technical_feature_payload(payload: dict[str, Any]) -> bool:
    return bool(payload) and set(payload).issubset(set(FEATURE_NAMES))


def clinical_data_to_features(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Converte JSON clinico simples gerado pela IA para features do modelo."""
    if isinstance(payload.get("features"), dict):
        technical_features = payload["features"]
        if _is_technical_feature_payload(technical_features):
            return technical_features

    if _is_technical_feature_payload(payload):
        return payload

    age = _to_int(payload.get("idade") or payload.get("idade_anos"))
    if age is None or not 10 <= age <= 120:
        return None

    features = {name: 0 for name in FEATURE_NAMES}
    features["CO_IDADE_PACIENTE_NUM"] = age
    features["CO_TEMPO_MAMO_ANTERIOR_NUM"] = _mammogram_time_code_from_value(
        payload.get("tempo_mamografia_anterior_codigo")
        or payload.get("tempo_desde_ultima_mamografia_codigo")
        or payload.get("tempo_mamografia_anterior_meses")
        or payload.get("tempo_desde_ultima_mamografia_meses")
        or payload.get("tempo_mamografia_anterior")
        or payload.get("tempo_desde_ultima_mamografia")
    )

    sex = _normalized(str(payload.get("sexo") or "ignorado"))
    if sex.startswith("f") or "mulher" in sex:
        selected_sex = "SG_SEXO_F"
    elif sex.startswith("m") or "homem" in sex:
        selected_sex = "SG_SEXO_M"
    else:
        selected_sex = "SG_SEXO_I"
    _one_hot(features, selected_sex, ["SG_SEXO_F", "SG_SEXO_I", "SG_SEXO_M"])

    race = _detect_race(
        _normalized(str(payload.get("raca_cor") or payload.get("raca") or ""))
    )
    if race is not None:
        _one_hot(
            features,
            race,
            [
                "CO_RACA_COR_01",
                "CO_RACA_COR_02",
                "CO_RACA_COR_03",
                "CO_RACA_COR_04",
                "CO_RACA_COR_05",
            ],
        )

    elevated_risk = _to_bool(
        payload.get("risco_elevado")
        if "risco_elevado" in payload
        else payload.get("historico_familiar")
    )
    _one_hot(
        features,
        {
            True: "TP_RESP_APRES_RISC_ELEV_CANCER_01",
            False: "TP_RESP_APRES_RISC_ELEV_CANCER_02",
            None: "TP_RESP_APRES_RISC_ELEV_CANCER_03",
        }[elevated_risk],
        [
            "TP_RESP_APRES_RISC_ELEV_CANCER_01",
            "TP_RESP_APRES_RISC_ELEV_CANCER_02",
            "TP_RESP_APRES_RISC_ELEV_CANCER_03",
        ],
    )

    professional_exam = _to_bool(payload.get("exame_mamas_profissional"))
    _one_hot(
        features,
        {
            True: "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01",
            False: "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02",
            None: "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03",
        }[professional_exam],
        [
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01",
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02",
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03",
        ],
    )

    mammogram_ever = _to_bool(payload.get("mamografia_previa"))
    _one_hot(
        features,
        {
            True: "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01",
            False: "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02",
            None: "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03",
        }[mammogram_ever],
        [
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01",
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02",
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03",
        ],
    )

    indication = _normalized(str(payload.get("indicacao") or ""))
    if any(term in indication for term in ["diagnost", "sintoma", "investig"]):
        _one_hot(features, "CO_IND_CLINICA_02", ["CO_IND_CLINICA_01", "CO_IND_CLINICA_02"])
        mammography_type = "TP_MAMOGRAFIA_RASTREAMENT_02"
    else:
        _one_hot(features, "CO_IND_CLINICA_01", ["CO_IND_CLINICA_01", "CO_IND_CLINICA_02"])
        mammography_type = (
            "TP_MAMOGRAFIA_RASTREAMENT_01"
            if "rastream" in indication or "rotina" in indication
            else "TP_MAMOGRAFIA_RASTREAMENT_03"
        )

    _one_hot(
        features,
        mammography_type,
        [
            "TP_MAMOGRAFIA_RASTREAMENT_01",
            "TP_MAMOGRAFIA_RASTREAMENT_02",
            "TP_MAMOGRAFIA_RASTREAMENT_03",
        ],
    )

    return features


def extract_clinical_json_from_text(text: str) -> dict[str, Any] | None:
    return _extract_json_object(text)


def _extract_natural_language_features(text: str) -> dict[str, Any] | None:
    normalized = _normalized(text)
    age = _extract_age(normalized)
    if age is None:
        return None

    features = {name: 0 for name in FEATURE_NAMES}
    features["CO_IDADE_PACIENTE_NUM"] = age
    features["CO_TEMPO_MAMO_ANTERIOR_NUM"] = _extract_previous_mammogram_time(normalized)

    _one_hot(
        features,
        _detect_sex(normalized),
        ["SG_SEXO_F", "SG_SEXO_I", "SG_SEXO_M"],
    )

    race = _detect_race(normalized)
    if race is not None:
        _one_hot(
            features,
            race,
            [
                "CO_RACA_COR_01",
                "CO_RACA_COR_02",
                "CO_RACA_COR_03",
                "CO_RACA_COR_04",
                "CO_RACA_COR_05",
            ],
        )

    elevated_risk = _detect_yes_no_unknown(
        normalized,
        yes_terms=[
            "risco elevado",
            "alto risco",
            "historia familiar",
            "historico familiar",
            "brca",
            "mutacao",
        ],
        no_terms=[
            "sem risco elevado",
            "nega risco elevado",
            "sem historia familiar",
            "nega historia familiar",
        ],
        yes_feature="TP_RESP_APRES_RISC_ELEV_CANCER_01",
        no_feature="TP_RESP_APRES_RISC_ELEV_CANCER_02",
        unknown_feature="TP_RESP_APRES_RISC_ELEV_CANCER_03",
    )
    _one_hot(
        features,
        elevated_risk,
        [
            "TP_RESP_APRES_RISC_ELEV_CANCER_01",
            "TP_RESP_APRES_RISC_ELEV_CANCER_02",
            "TP_RESP_APRES_RISC_ELEV_CANCER_03",
        ],
    )

    professional_exam = _detect_yes_no_unknown(
        normalized,
        yes_terms=[
            "exame clinico das mamas",
            "exame das mamas",
            "exame por profissional",
            "examinada por profissional",
        ],
        no_terms=[
            "nunca fez exame clinico",
            "sem exame clinico",
            "nao fez exame das mamas",
        ],
        yes_feature="TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01",
        no_feature="TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02",
        unknown_feature="TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03",
    )
    _one_hot(
        features,
        professional_exam,
        [
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_01",
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_02",
            "TP_RESP_ANT_MAMA_EXA_PROF_SAUD_03",
        ],
    )

    mammogram_ever = _detect_yes_no_unknown(
        normalized,
        yes_terms=[
            "ja fez mamografia",
            "mamografia previa",
            "mamografia anterior",
            "ultima mamografia",
        ],
        no_terms=[
            "nunca fez mamografia",
            "sem mamografia previa",
            "nao fez mamografia",
        ],
        yes_feature="TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01",
        no_feature="TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02",
        unknown_feature="TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03",
    )
    _one_hot(
        features,
        mammogram_ever,
        [
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_01",
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_02",
            "TP_RESP_FEZ_MAMOGRA_ALGUMA_VEZ_03",
        ],
    )

    screening_terms = ["rastreamento", "rotina", "screening", "assintomatica"]
    diagnostic_terms = ["nodulo", "dor", "secrecao", "alteracao", "sintoma", "diagnostica"]
    if _has_affirmed_term(normalized, diagnostic_terms):
        _one_hot(features, "CO_IND_CLINICA_02", ["CO_IND_CLINICA_01", "CO_IND_CLINICA_02"])
        _one_hot(
            features,
            "TP_MAMOGRAFIA_RASTREAMENT_02",
            [
                "TP_MAMOGRAFIA_RASTREAMENT_01",
                "TP_MAMOGRAFIA_RASTREAMENT_02",
                "TP_MAMOGRAFIA_RASTREAMENT_03",
            ],
        )
    else:
        _one_hot(features, "CO_IND_CLINICA_01", ["CO_IND_CLINICA_01", "CO_IND_CLINICA_02"])
        screening_feature = (
            "TP_MAMOGRAFIA_RASTREAMENT_01"
            if any(term in normalized for term in screening_terms)
            else "TP_MAMOGRAFIA_RASTREAMENT_03"
        )
        _one_hot(
            features,
            screening_feature,
            [
                "TP_MAMOGRAFIA_RASTREAMENT_01",
                "TP_MAMOGRAFIA_RASTREAMENT_02",
                "TP_MAMOGRAFIA_RASTREAMENT_03",
            ],
        )

    return features


def extract_features_from_text(text: str) -> dict[str, Any] | None:
    """Extrai features do texto livre ou de um objeto JSON enviado na mensagem."""
    payload = extract_clinical_json_from_text(text)
    if payload is not None:
        features = clinical_data_to_features(payload)
        if features is not None:
            return features

    return _extract_natural_language_features(text)


@tool
def prever_risco_cancer_mama(features: dict[str, Any]) -> dict[str, Any]:
    """
    Chama a API Random Forest local para estimar risco academico de cancer de mama.
    Use somente quando houver um dicionario completo de features estruturadas.
    """
    response = httpx.post(
        f"{settings.ml_api_url}/predict",
        json={"features": features},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
