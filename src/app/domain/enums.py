from enum import Enum


class DiagnosisStatus(int, Enum):
    NEGATIVE = 0
    POSITIVE = 1


class ModelType(str, Enum):
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
