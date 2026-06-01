"""Synthetic trip-level data for end-to-end demos before real datasets arrive."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import MODEL_FEATURES, STYLE_LABELS


def _bounded(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(values, low, high)


def generate_trip_samples(n_samples: int = 800, random_state: int = 42) -> pd.DataFrame:
    """Generate trip-level feature rows matching the PDF project schema."""

    rng = np.random.default_rng(random_state)
    labels = rng.choice(STYLE_LABELS, size=n_samples, p=[0.55, 0.30, 0.15])
    rows = []

    for trip_id, label in enumerate(labels, start=1):
        if label == "normal":
            speed_mean = rng.normal(42, 9)
            accel_base = rng.normal(0.85, 0.25)
            brake_base = rng.normal(0.75, 0.22)
            yaw_base = rng.normal(6.0, 2.0)
            event_scale = rng.poisson(1)
            rpm_mean = rng.normal(1850, 260)
            engine_load = rng.normal(42, 9)
            coolant = rng.normal(88, 4)
            battery = rng.normal(12.7, 0.18)
            idle_time = rng.normal(5, 3)
        elif label == "aggressive":
            speed_mean = rng.normal(57, 12)
            accel_base = rng.normal(1.85, 0.45)
            brake_base = rng.normal(1.65, 0.45)
            yaw_base = rng.normal(12.0, 3.5)
            event_scale = rng.poisson(4)
            rpm_mean = rng.normal(2650, 420)
            engine_load = rng.normal(63, 12)
            coolant = rng.normal(94, 5)
            battery = rng.normal(12.45, 0.25)
            idle_time = rng.normal(8, 5)
        else:
            speed_mean = rng.normal(68, 15)
            accel_base = rng.normal(2.55, 0.65)
            brake_base = rng.normal(2.35, 0.65)
            yaw_base = rng.normal(17.0, 5.0)
            event_scale = rng.poisson(7)
            rpm_mean = rng.normal(3350, 620)
            engine_load = rng.normal(78, 12)
            coolant = rng.normal(101, 7)
            battery = rng.normal(12.20, 0.35)
            idle_time = rng.normal(12, 7)

        trip_duration = float(_bounded(rng.normal(42, 16), 10, 120))
        hard_accel_count = int(max(0, event_scale + rng.poisson(max(accel_base - 0.5, 0.1))))
        hard_brake_count = int(max(0, event_scale + rng.poisson(max(brake_base - 0.5, 0.1))))
        sharp_turn_count = int(max(0, rng.poisson(max(yaw_base / 5.0 - 1.0, 0.1))))
        high_rpm_minutes = float(_bounded(rng.normal(max(rpm_mean - 2400, 0) / 260, 1.5), 0, 25))

        if rng.random() < 0.08:
            coolant += rng.uniform(10, 20)
        if rng.random() < 0.08:
            battery -= rng.uniform(0.45, 0.95)
        if rng.random() < 0.07:
            engine_load += rng.uniform(15, 25)

        row = {
            "trip_id": f"trip_{trip_id:04d}",
            "speed_mean": float(_bounded(speed_mean, 5, 130)),
            "speed_max": float(_bounded(speed_mean + rng.normal(24, 8), 20, 170)),
            "acceleration_mean": float(_bounded(accel_base * 0.45, 0.05, 3.0)),
            "acceleration_max": float(_bounded(accel_base + rng.normal(1.1, 0.35), 0.2, 5.0)),
            "brake_intensity_mean": float(_bounded(brake_base * 0.42, 0.05, 3.0)),
            "brake_intensity_max": float(_bounded(brake_base + rng.normal(1.0, 0.35), 0.2, 5.0)),
            "jerk_mean": float(_bounded((accel_base + brake_base) / 2.8, 0.05, 3.0)),
            "jerk_max": float(_bounded((accel_base + brake_base) + rng.normal(0.7, 0.25), 0.2, 6.0)),
            "yaw_rate_mean": float(_bounded(yaw_base * 0.45, 0.5, 25)),
            "yaw_rate_max": float(_bounded(yaw_base + rng.normal(8, 3), 3, 45)),
            "rpm_mean": float(_bounded(rpm_mean, 700, 5200)),
            "rpm_max": float(_bounded(rpm_mean + rng.normal(1200, 420), 1000, 6800)),
            "engine_load_mean": float(_bounded(engine_load, 10, 100)),
            "engine_load_max": float(_bounded(engine_load + rng.normal(18, 8), 25, 100)),
            "coolant_temp_mean": float(_bounded(coolant, 70, 125)),
            "coolant_temp_max": float(_bounded(coolant + rng.normal(6, 3), 78, 130)),
            "battery_voltage_mean": float(_bounded(battery, 10.5, 14.2)),
            "battery_voltage_min": float(_bounded(battery - rng.normal(0.25, 0.12), 9.5, 13.5)),
            "trip_duration": trip_duration,
            "hard_accel_count": hard_accel_count,
            "hard_brake_count": hard_brake_count,
            "sharp_turn_count": sharp_turn_count,
            "high_rpm_minutes": high_rpm_minutes,
            "idle_time": float(_bounded(idle_time, 0, trip_duration * 0.75)),
            "driving_style": label,
        }

        anomaly_score = 0
        anomaly_score += row["coolant_temp_max"] > 108
        anomaly_score += row["battery_voltage_min"] < 11.8
        anomaly_score += row["engine_load_max"] > 92
        anomaly_score += row["rpm_max"] > 5600
        row["vehicle_anomaly_label"] = int(anomaly_score >= 1)
        rows.append(row)

    df = pd.DataFrame(rows)
    return df[["trip_id", *MODEL_FEATURES, "driving_style", "vehicle_anomaly_label"]]


def train_test_split(
    frame: pd.DataFrame,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Small deterministic train/test splitter without sklearn."""

    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    shuffled = frame.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    test_count = max(1, int(len(shuffled) * test_size))
    test = shuffled.iloc[:test_count].reset_index(drop=True)
    train = shuffled.iloc[test_count:].reset_index(drop=True)
    return train, test
