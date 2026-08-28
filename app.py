from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from droneguard.data import enrich_telemetry, load_telemetry, validate_telemetry
from droneguard.detection import HybridDetector
from droneguard.experiments import sampling_rate_experiment
from droneguard.simulation import SCENARIOS, SimulationConfig, make_training_dataset, simulate

st.set_page_config(page_title="DroneGuard", page_icon="🛩️", layout="wide")
st.title("DroneGuard")
st.caption("Physics-informed digital twin and anomaly detection for drone telemetry")

ORIGINAL_DATA = (
    Path(__file__).parent
    / "data(this folder contains all the data collected for analysis"
    / "integrated_telemetry_60s.csv"
)


@st.cache_resource
def build_detector() -> HybridDetector:
    training = make_training_dataset(SimulationConfig(duration_s=24, sampling_hz=20, seed=17))
    return HybridDetector().fit(training)

with st.sidebar:
    st.header("Data source")
    source = st.radio(
        "Choose a source",
        ["Original ESP32 recording", "Digital twin", "Upload compatible CSV"],
    )
    if source == "Digital twin":
        scenario = st.selectbox("Scenario", SCENARIOS)
        duration = st.slider("Duration (seconds)", 10, 120, 45)
        frequency = st.select_slider("Sampling frequency (Hz)", [2, 5, 10, 20, 50, 100], value=20)
        noise = st.slider("Sensor noise", 0.1, 3.0, 1.0, 0.1)
        seed = st.number_input("Random seed", 0, 10000, 42)
        frame = simulate(scenario, SimulationConfig(duration_s=duration, sampling_hz=frequency, noise_scale=noise, seed=int(seed)))
        source_badge = "SIMULATED FLIGHT DATA"
    elif source == "Original ESP32 recording":
        if not ORIGINAL_DATA.exists():
            st.error("The original ESP32 CSV was not found in this repository.")
            st.stop()
        frame = load_telemetry(ORIGINAL_DATA)
        source_badge = "REAL BENCH DATA — NOT REAL FLIGHT DATA"
    else:
        upload = st.file_uploader("Upload telemetry CSV", type=["csv"])
        if upload is None:
            st.info("Upload a CSV with the same columns as the original ESP32 dataset.")
            st.stop()
        try:
            frame = load_telemetry(upload)
        except ValueError as error:
            st.error(str(error)); st.stop()
        source_badge = "REAL BENCH DATA — NOT REAL FLIGHT DATA"

st.markdown(f"**Data provenance:** `{source_badge}`")

try:
    quality = validate_telemetry(frame)
except ValueError as error:
    st.error(str(error)); st.stop()

detector = build_detector()
prediction = detector.predict(frame)
enriched = enrich_telemetry(frame)

tab_overview, tab_telemetry, tab_risk, tab_twin, tab_experiment, tab_report = st.tabs([
    "Mission overview", "Telemetry explorer", "Risk analysis", "Digital twin",
    "Sampling experiment", "Report",
])

with tab_overview:
    cols = st.columns(5)
    cols[0].metric("Samples", quality.rows)
    cols[1].metric("Duration", f"{quality.duration_s:.1f} s")
    cols[2].metric("Sampling rate", f"{quality.sampling_hz:.2f} Hz")
    cols[3].metric("Peak acceleration", f"{frame.accel_magnitude.max():.2f} m/s²")
    cols[4].metric("High-risk samples", int((prediction.risk_level == "HIGH").sum()))
    st.subheader("Data quality")
    st.json({k: v for k, v in quality.as_dict().items() if k != "warnings"})
    for warning in quality.warnings:
        st.warning(warning)

with tab_telemetry:
    acceleration = enriched.melt("time_s", ["accel_x", "accel_y", "accel_z", "accel_magnitude"], var_name="channel", value_name="value")
    st.plotly_chart(px.line(acceleration, x="time_s", y="value", color="channel", title="Acceleration telemetry"), width="stretch")
    angular = enriched.melt("time_s", ["gyro_x", "gyro_y", "gyro_z"], var_name="channel", value_name="value")
    st.plotly_chart(px.line(angular, x="time_s", y="value", color="channel", title="Angular-rate telemetry"), width="stretch")
    st.plotly_chart(px.line(enriched, x="time_s", y="ina240_out_voltage", title="INA240 analogue output (uncalibrated)"), width="stretch")

with tab_risk:
    risk = go.Figure()
    risk.add_trace(go.Scatter(x=prediction.time_ms / 1000, y=prediction.risk_score, name="Hybrid risk score"))
    risk.add_hline(y=.65, line_dash="dash", line_color="red", annotation_text="High-risk threshold")
    risk.update_layout(title="Risk timeline", xaxis_title="Time (s)", yaxis_title="Risk score", yaxis_range=[0, 1])
    st.plotly_chart(risk, width="stretch")
    events = prediction.loc[prediction.risk_level != "LOW", ["time_ms", "predicted_state", "confidence", "risk_score", "risk_level"]]
    st.dataframe(events.head(250), width="stretch")
    st.caption("MODEL INFERENCE — experimental decision support, not a certified flight-safety diagnosis.")

with tab_twin:
    if "simulated_current_a" in frame:
        cols = st.columns(3)
        cols[0].metric("Minimum simulated SOC", f"{frame.simulated_soc.min()*100:.1f}%")
        cols[1].metric("Peak simulated current", f"{frame.simulated_current_a.max():.2f} A")
        cols[2].metric("Minimum simulated voltage", f"{frame.simulated_battery_v.min():.2f} V")
        energy = frame.melt("time_ms", ["simulated_current_a", "simulated_battery_v", "simulated_soc"], var_name="variable", value_name="value")
        st.plotly_chart(px.line(energy, x="time_ms", y="value", color="variable", facet_row="variable", title="Simulated energy system"), width="stretch")
    else:
        st.info("Energy-state values are shown only for digital-twin data. The original INA240 output is uncalibrated and is not converted to amperes.")

with tab_experiment:
    st.write("This experiment trains on 20 Hz simulated missions and evaluates independent missions at six sampling rates.")
    if st.button("Run reproducible sampling-rate experiment"):
        with st.spinner("Running experiment..."):
            result = sampling_rate_experiment()
        st.dataframe(result, width="stretch")
        st.plotly_chart(px.line(result, x="sampling_hz", y="macro_f1", markers=True, log_x=True, range_y=[0, 1], title="Sampling rate vs macro F1"), width="stretch")

with tab_report:
    summary = f"""# DroneGuard Telemetry Health Report

Data provenance: {source_badge}

- Samples: {quality.rows}
- Duration: {quality.duration_s:.2f} seconds
- Estimated sampling rate: {quality.sampling_hz:.3f} Hz
- Missing values: {quality.missing_values}
- Duplicate timestamps: {quality.duplicate_timestamps}
- High-risk samples: {int((prediction.risk_level == 'HIGH').sum())}
- Maximum risk score: {prediction.risk_score.max():.3f}

## Limitations

The original INA240 signal is an uncalibrated analogue output and must not be reported as amperes. Simulated results are not real flight measurements. Model outputs are experimental and are not certified flight-safety diagnoses.
"""
    st.markdown(summary)
    st.download_button("Download report", summary, "droneguard_report.md", "text/markdown")
    st.download_button("Download analysed telemetry", prediction.to_csv(index=False), "analysed_telemetry.csv", "text/csv")
