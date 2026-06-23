from __future__ import annotations

import logging
from functools import lru_cache

from minha_api.schemas import FeatureContribution, PatientData
from minha_api.services.llm.base import LLMProvider
from minha_api.services.llm.factory import create_llm_provider

logger = logging.getLogger(__name__)

# System prompt: define persona clínica e regras de saída
_SYSTEM_PROMPT = """Você é um assistente clínico especializado em endocrinologia reprodutiva e Síndrome dos Ovários Policísticos (SOP/PCOS). Seu papel é interpretar resultados de modelos de machine learning e traduzi-los em linguagem clínica clara e acionável para médicos especialistas.

Diretrizes obrigatórias:
- Use terminologia médica precisa e português do Brasil.
- Baseie-se exclusivamente nos dados fornecidos — não especule além das evidências.
- Estruture a resposta em três parágrafos curtos: (1) interpretação do resultado, (2) análise dos fatores determinantes, (3) sugestão de próximos passos clínicos.
- Máximo 250 palavras no total.
- Apresente o diagnóstico como probabilidade — nunca como certeza absoluta.
- Ressalte que o modelo é ferramenta de triagem, não substitui avaliação especializada.
- Para próximos passos, considere: ultrassonografia pélvica, perfil hormonal completo (FSH, LH, testosterona total/livre, DHEA-S, androstenediona), glicemia de jejum e insulina basal, se aplicável."""

# Mapeamento de nomes internos (com prefixo do ColumnTransformer) → rótulo legível
_FEATURE_LABELS: dict[str, str] = {
    "num__Follicle No. (R)": "Número de folículos (ovário direito)",
    "num__Follicle No. (L)": "Número de folículos (ovário esquerdo)",
    "num__Cycle(R/I)": "Padrão do ciclo menstrual",
    "num__AMH(ng/mL)": "Hormônio Antimülleriano (AMH)",
    "num__BMI": "IMC",
    "num__Cycle length(days)": "Duração do ciclo",
    "num__ Age (yrs)": "Idade",
    "num__Hip(inch)": "Circunferência do quadril",
    "num__Avg. F size (L) (mm)": "Tamanho médio dos folículos (esq.)",
    "num__Marraige Status (Yrs)": "Anos de casamento",
    "num__Endometrium (mm)": "Espessura do endométrio",
    "num__Avg. F size (R) (mm)": "Tamanho médio dos folículos (dir.)",
    "num__Pulse rate(bpm) ": "Frequência cardíaca",
    "num__Hb(g/dl)": "Hemoglobina",
    "bin__Skin darkening (Y/N)": "Acantose nigricans",
    "bin__hair growth(Y/N)": "Hirsutismo",
    "bin__Weight gain(Y/N)": "Ganho de peso",
    "bin__Fast food (Y/N)": "Consumo de fast food",
    "bin__Pimples(Y/N)": "Acne",
    "bin__Hair loss(Y/N)": "Alopecia androgenética",
}


def _readable_feature(name: str) -> str:
    return _FEATURE_LABELS.get(name, name)


def _format_contributions(features: list[FeatureContribution]) -> str:
    lines = []
    for feat in features:
        label = _readable_feature(feat.feature)
        arrow = "↑ favorece SOP" if feat.direction == "positiva" else "↓ reduz probabilidade de SOP"
        lines.append(f"  • {label}: {arrow} (peso SHAP: {feat.contribution:+.4f})")
    return "\n".join(lines)


def _build_user_prompt(patient: PatientData, result: dict) -> str:
    diagnosis_str = "POSITIVO para SOP" if result["diagnosis"] else "NEGATIVO para SOP"
    prob_pct = result["probability"] * 100
    cycle_str = "Irregular" if patient.cycle > 2 else "Regular"

    symptoms = [
        label
        for flag, label in [
            (patient.hair_growth, "Hirsutismo"),
            (patient.skin_darkening, "Acantose nigricans"),
            (patient.pimples, "Acne"),
            (patient.hair_loss, "Alopecia"),
            (patient.weight_gain, "Ganho de peso"),
        ]
        if flag
    ]
    symptoms_str = ", ".join(symptoms) if symptoms else "Nenhum relatado"

    features_block = _format_contributions(result["top_contributing_features"])

    return f"""## Resultado do modelo de triagem — SOP

**Diagnóstico:** {diagnosis_str}
**Probabilidade estimada:** {prob_pct:.1f}%
**Nível de confiança:** {result["confidence"]}

**Top 5 fatores determinantes (análise SHAP):**
{features_block}

**Resumo clínico da paciente:**
- Idade: {patient.age:.0f} anos | IMC: {patient.bmi:.1f} kg/m²
- Ciclo: {cycle_str} ({patient.cycle_length:.0f} dias)
- AMH: {patient.amh:.2f} ng/mL
- Folículos (dir./esq.): {patient.follicle_no_r:.0f} / {patient.follicle_no_l:.0f}
- Tamanho folicular médio (dir./esq.): {patient.avg_f_size_r:.1f} mm / {patient.avg_f_size_l:.1f} mm
- Endométrio: {patient.endometrium:.1f} mm | Hb: {patient.hb:.1f} g/dL
- Sintomas hiperandrogênicos: {symptoms_str}

Com base nesses dados, forneça a interpretação clínica estruturada conforme suas diretrizes."""


@lru_cache(maxsize=1)
def _get_provider() -> LLMProvider:
    return create_llm_provider()


def interpret(patient: PatientData, prediction_result: dict) -> str:
    try:
        provider = _get_provider()
        user_prompt = _build_user_prompt(patient, prediction_result)
        return provider.generate(_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        logger.warning("Falha na interpretação LLM (%s): %s", type(exc).__name__, exc)
        prob_pct = prediction_result["probability"] * 100
        diagnosis_str = "positivo" if prediction_result["diagnosis"] else "negativo"
        return (
            f"Resultado {diagnosis_str} para SOP com probabilidade de {prob_pct:.1f}% "
            f"(confiança: {prediction_result['confidence']}). "
            "Interpretação detalhada indisponível — verifique a configuração do provedor LLM "
            "e as variáveis de ambiente (LLM_PROVIDER, *_API_KEY)."
        )
