from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ["accel_magnitude", "gyro_magnitude", "jerk", "dynamic_acceleration", "ina240_out_voltage"]


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["gyro_magnitude"] = np.sqrt(result.gyro_x**2 + result.gyro_y**2 + result.gyro_z**2)
    seconds = result.time_ms / 1000
    result["jerk"] = result.accel_magnitude.diff().div(seconds.diff().replace(0, np.nan)).fillna(0).clip(-100, 100)
    baseline = result.accel_magnitude.iloc[: max(10, len(result)//10)].median()
    result["dynamic_acceleration"] = (result.accel_magnitude - baseline).abs()
    return result.replace([np.inf, -np.inf], np.nan).ffill().bfill().fillna(0)


class HybridDetector:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.unsupervised = Pipeline([
            ("scale", StandardScaler()),
            ("model", IsolationForest(contamination=.08, random_state=random_state)),
        ])
        self.classifier = RandomForestClassifier(n_estimators=180, min_samples_leaf=3, class_weight="balanced", random_state=random_state)

    def fit(self, frame: pd.DataFrame) -> "HybridDetector":
        enriched = add_features(frame)
        normal = enriched[enriched.get("label", "normal") == "normal"]
        self.unsupervised.fit(normal[FEATURES])
        if "label" in enriched:
            self.classifier.fit(enriched[FEATURES], enriched.label)
        return self

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        enriched = add_features(frame)
        raw = -self.unsupervised.decision_function(enriched[FEATURES])
        anomaly = (raw - raw.min()) / (np.ptp(raw) + 1e-9)
        probabilities = self.classifier.predict_proba(enriched[FEATURES])
        classes = self.classifier.classes_
        predicted = classes[np.argmax(probabilities, axis=1)]
        confidence = np.max(probabilities, axis=1)
        rule = np.clip((enriched.dynamic_acceleration / 4) + (enriched.gyro_magnitude / 2), 0, 1)
        enriched["anomaly_score"] = anomaly
        enriched["rule_score"] = rule
        enriched["risk_score"] = np.clip(.45 * anomaly + .35 * rule + .20 * confidence * (predicted != "normal"), 0, 1)
        enriched["predicted_state"] = predicted
        enriched["confidence"] = confidence
        enriched["risk_level"] = pd.cut(enriched.risk_score, [-.01, .35, .65, 1.01], labels=["LOW", "MEDIUM", "HIGH"])
        return enriched


def evaluate(detector: HybridDetector, frame: pd.DataFrame) -> dict:
    predicted = detector.predict(frame)
    return {
        "classification_report": classification_report(frame.label, predicted.predicted_state, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(frame.label, predicted.predicted_state, labels=detector.classifier.classes_).tolist(),
        "classes": detector.classifier.classes_.tolist(),
    }

