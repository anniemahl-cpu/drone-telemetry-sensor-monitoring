from __future__ import annotations

import pandas as pd
from sklearn.metrics import f1_score

from .detection import HybridDetector
from .simulation import SCENARIOS, SimulationConfig, make_training_dataset, simulate


def sampling_rate_experiment(seed: int = 42) -> pd.DataFrame:
    training = make_training_dataset(SimulationConfig(duration_s=24, sampling_hz=20, seed=seed))
    detector = HybridDetector(seed).fit(training)
    rows = []
    for hz in [100, 50, 20, 10, 5, 2]:
        test = pd.concat([
            simulate(s, SimulationConfig(duration_s=20, sampling_hz=hz, seed=seed + 100 + i))
            for i, s in enumerate(SCENARIOS)
        ], ignore_index=True)
        prediction = detector.predict(test)
        rows.append({"sampling_hz": hz, "macro_f1": f1_score(test.label, prediction.predicted_state, average="macro", zero_division=0)})
    return pd.DataFrame(rows)

