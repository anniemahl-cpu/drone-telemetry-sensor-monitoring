import numpy as np

from droneguard.data import enrich_telemetry, validate_telemetry
from droneguard.detection import HybridDetector
from droneguard.simulation import SCENARIOS, SimulationConfig, make_training_dataset, simulate


def test_simulator_is_reproducible():
    config = SimulationConfig(duration_s=4, sampling_hz=10, seed=7)
    first = simulate("gust", config)
    second = simulate("gust", config)
    assert first.equals(second)
    assert len(first) == 40


def test_all_scenarios_generate_finite_sensor_data():
    for scenario in SCENARIOS:
        frame = simulate(scenario, SimulationConfig(duration_s=5, sampling_hz=10))
        assert len(frame) > 20
        assert np.isfinite(frame.accel_magnitude).all()


def test_validation_checks_formula_consistency():
    frame = simulate("normal", SimulationConfig(duration_s=5, sampling_hz=10))
    report = validate_telemetry(frame)
    assert report.sampling_hz == 10
    assert report.accel_magnitude_rmse < 1e-10
    assert report.voltage_rmse < 1e-10


def test_enrichment_and_detector():
    training = make_training_dataset(SimulationConfig(duration_s=8, sampling_hz=10))
    detector = HybridDetector().fit(training)
    output = detector.predict(simulate("thrust_loss", SimulationConfig(duration_s=8, sampling_hz=10, seed=99)))
    assert {"risk_score", "risk_level", "predicted_state"}.issubset(output.columns)
    assert output.risk_score.between(0, 1).all()
    assert "motion_state" in enrich_telemetry(simulate("normal", SimulationConfig(duration_s=5, sampling_hz=10))).columns

