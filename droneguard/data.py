from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, TextIO

import numpy as np
import pandas as pd

REQUIRED = (
    "time_ms", "accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y",
    "gyro_z", "accel_magnitude", "ina240_adc", "ina240_out_voltage",
)


@dataclass(frozen=True)
class DataQualityReport:
    rows: int
    duration_s: float
    sampling_hz: float
    missing_values: int
    duplicate_timestamps: int
    non_monotonic_timestamps: int
    accel_magnitude_rmse: float
    voltage_rmse: float
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, float | int | tuple[str, ...]]:
        return self.__dict__.copy()


def load_telemetry(source: str | Path | BinaryIO | TextIO) -> pd.DataFrame:
    frame = pd.read_csv(source)
    missing = [name for name in REQUIRED if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    frame = frame.loc[:, REQUIRED].copy()
    for column in REQUIRED:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def validate_telemetry(frame: pd.DataFrame) -> DataQualityReport:
    if frame.empty:
        raise ValueError("Telemetry file is empty")
    dt = frame["time_ms"].diff()
    positive_dt = dt[dt > 0]
    duration_s = max(0.0, (frame["time_ms"].iloc[-1] - frame["time_ms"].iloc[0]) / 1000)
    sampling_hz = 1000 / positive_dt.median() if len(positive_dt) else 0.0
    calculated_accel = np.sqrt(frame.accel_x**2 + frame.accel_y**2 + frame.accel_z**2)
    calculated_voltage = frame.ina240_adc * 3.3 / 4095.0
    accel_rmse = float(np.sqrt(np.nanmean((calculated_accel - frame.accel_magnitude) ** 2)))
    voltage_rmse = float(np.sqrt(np.nanmean((calculated_voltage - frame.ina240_out_voltage) ** 2)))
    warnings: list[str] = []
    if sampling_hz < 10:
        warnings.append("Low sampling rate: suitable for broad motion states, not motor vibration or flight control.")
    if duration_s < 120:
        warnings.append("Short recording: treat model results as a prototype, not a flight-safety validation.")
    if frame.ina240_out_voltage.max() - frame.ina240_out_voltage.min() < 0.05:
        warnings.append("INA240 output has a narrow range and remains uncalibrated; do not report amperes.")
    if int(frame.isna().sum().sum()):
        warnings.append("Missing values were detected.")
    return DataQualityReport(
        rows=len(frame), duration_s=float(duration_s), sampling_hz=float(sampling_hz),
        missing_values=int(frame.isna().sum().sum()),
        duplicate_timestamps=int(frame.time_ms.duplicated().sum()),
        non_monotonic_timestamps=int((dt.dropna() <= 0).sum()),
        accel_magnitude_rmse=accel_rmse, voltage_rmse=voltage_rmse,
        warnings=tuple(warnings),
    )


def enrich_telemetry(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["time_s"] = (result.time_ms - result.time_ms.iloc[0]) / 1000
    result["gyro_magnitude"] = np.sqrt(result.gyro_x**2 + result.gyro_y**2 + result.gyro_z**2)
    dt = result.time_s.diff().replace(0, np.nan)
    result["jerk"] = result.accel_magnitude.diff().div(dt).fillna(0)
    baseline = float(result.accel_magnitude.iloc[: max(5, len(result)//10)].median())
    result["dynamic_acceleration"] = (result.accel_magnitude - baseline).abs()
    window = max(3, min(11, len(result)//10 if len(result) >= 30 else 3))
    result["motion_score"] = (
        result.dynamic_acceleration.rolling(window, center=True, min_periods=1).mean()
        + 2 * result.gyro_magnitude.rolling(window, center=True, min_periods=1).mean()
    )
    median = result.motion_score.median()
    mad = np.median(np.abs(result.motion_score - median)) or 1e-6
    result["motion_state"] = np.where(result.motion_score > median + 4 * mad, "dynamic", "stationary")
    return result

