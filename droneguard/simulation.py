from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimulationConfig:
    duration_s: float = 60.0
    sampling_hz: float = 50.0
    mass_kg: float = 1.2
    battery_capacity_ah: float = 2.2
    initial_soc: float = 1.0
    noise_scale: float = 1.0
    seed: int = 42


SCENARIOS = (
    "normal", "gust", "aggressive_manoeuvre", "thrust_loss",
    "battery_sag", "current_spike", "imu_bias", "sensor_freeze", "packet_loss",
)


def simulate(scenario: str = "normal", config: SimulationConfig | None = None) -> pd.DataFrame:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    cfg = config or SimulationConfig()
    rng = np.random.default_rng(cfg.seed)
    dt = 1 / cfg.sampling_hz
    t = np.arange(0, cfg.duration_s, dt)
    n = len(t)
    event_start, event_end = cfg.duration_s * 0.45, cfg.duration_s * 0.65
    event = (t >= event_start) & (t <= event_end)
    phase = 2 * np.pi * 0.35 * t
    ax = rng.normal(0, .025 * cfg.noise_scale, n)
    ay = rng.normal(0, .025 * cfg.noise_scale, n)
    az = 9.81 + rng.normal(0, .04 * cfg.noise_scale, n)
    gx = rng.normal(0, .006 * cfg.noise_scale, n)
    gy = rng.normal(0, .006 * cfg.noise_scale, n)
    gz = rng.normal(0, .008 * cfg.noise_scale, n)
    current = 7.0 + .35 * np.sin(phase) + rng.normal(0, .12 * cfg.noise_scale, n)
    label = np.full(n, "normal", dtype=object)

    if scenario == "gust":
        ax[event] += 2.0 * np.sin(phase[event] * 2); gy[event] += .45 * np.cos(phase[event]); label[event] = scenario
    elif scenario == "aggressive_manoeuvre":
        ax[event] += 3.2 * np.sin(phase[event]); ay[event] += 2.4 * np.cos(phase[event]); gz[event] += 1.1; current[event] += 4; label[event] = scenario
    elif scenario == "thrust_loss":
        az[event] -= 3.6; gx[event] += np.linspace(0, 1.3, event.sum()); current[event] -= 2.4; label[event] = scenario
    elif scenario == "battery_sag":
        current[event] += 4.5; label[event] = scenario
    elif scenario == "current_spike":
        current[event] += 10 + 2 * np.sin(phase[event] * 4); label[event] = scenario
    elif scenario == "imu_bias":
        ax[event] += np.linspace(0, 2.2, event.sum()); gy[event] += np.linspace(0, .55, event.sum()); label[event] = scenario
    elif scenario == "sensor_freeze":
        indices = np.flatnonzero(event); start = indices[0]
        for array in (ax, ay, az, gx, gy, gz): array[indices] = array[start]
        label[event] = scenario
    elif scenario == "packet_loss":
        label[event] = scenario

    power_factor = np.clip(current / max(current.max(), 1), 0, 1)
    used_ah = np.cumsum(current) * dt / 3600
    soc = np.clip(cfg.initial_soc - used_ah / cfg.battery_capacity_ah, 0, 1)
    open_voltage = 13.2 + 3.6 * soc
    terminal_voltage = open_voltage - current * 0.035 - (2.0 * power_factor if scenario == "battery_sag" else 0)
    accel_mag = np.sqrt(ax**2 + ay**2 + az**2)
    frame = pd.DataFrame({
        "time_ms": np.round(t * 1000).astype(int), "accel_x": ax, "accel_y": ay,
        "accel_z": az, "gyro_x": gx, "gyro_y": gy, "gyro_z": gz,
        "accel_magnitude": accel_mag, "simulated_current_a": current,
        "simulated_battery_v": terminal_voltage, "simulated_soc": soc,
        "label": label, "source": "SIMULATED_FLIGHT_DATA",
    })
    frame["ina240_adc"] = np.clip(np.round(1885 + (current - 7) * 8), 0, 4095).astype(int)
    frame["ina240_out_voltage"] = frame.ina240_adc * 3.3 / 4095
    if scenario == "packet_loss":
        drop = event & (rng.random(n) < .45)
        frame = frame.loc[~drop].reset_index(drop=True)
    return frame


def make_training_dataset(config: SimulationConfig | None = None) -> pd.DataFrame:
    cfg = config or SimulationConfig(duration_s=30, sampling_hz=20)
    frames = []
    for i, scenario in enumerate(SCENARIOS):
        frames.append(simulate(scenario, SimulationConfig(**{**cfg.__dict__, "seed": cfg.seed + i})))
    return pd.concat(frames, ignore_index=True)

