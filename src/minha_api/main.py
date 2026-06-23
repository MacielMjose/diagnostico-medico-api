from fastapi import FastAPI, HTTPException

from minha_api.models.pcos_classifier import predict
from minha_api.schemas import DiagnosisResponse, PatientData
from minha_api.services.interpreter import interpret

app = FastAPI(
    title="Diagnóstico Médico — SOP/PCOS",
    version="0.2.0",
    docs_url="/swagger",
    description=(
        "API de suporte diagnóstico para Síndrome dos Ovários Policísticos (SOP/PCOS). "
        "Combina Regressão Logística (scikit-learn) com explicabilidade SHAP e "
        "interpretação em linguagem natural via LLM."
    ),
)


@app.get("/")
def root():
    return {"status": "ok", "message": "API de Diagnóstico Médico funcionando!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/diagnose", response_model=DiagnosisResponse, summary="Diagnóstico de SOP")
def diagnose(patient: PatientData):
    """
    Recebe dados clínicos e laboratoriais de uma paciente, retorna:
    - Diagnóstico (positivo/negativo para SOP)
    - Probabilidade e nível de confiança
    - Top 5 fatores com análise SHAP
    - Interpretação em linguagem clínica gerada por LLM
    """
    try:
        patient_row = patient.to_dataframe_row()
        prediction_result = predict(patient_row)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro no modelo preditivo: {exc}")

    interpretation = interpret(patient, prediction_result)

    return DiagnosisResponse(
        diagnosis=prediction_result["diagnosis"],
        probability=prediction_result["probability"],
        confidence=prediction_result["confidence"],
        top_contributing_features=prediction_result["top_contributing_features"],
        interpretation=interpretation,
    )
