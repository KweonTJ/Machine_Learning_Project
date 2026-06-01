"""Event extraction from trip-level features."""

from __future__ import annotations

import pandas as pd


def detect_events(row: pd.Series) -> dict[str, float | int | bool]:
    """Translate numeric trip features into named driving/vehicle events."""

    events = {
        "hard_accel_count": int(row.get("hard_accel_count", 0)),
        "hard_brake_count": int(row.get("hard_brake_count", 0)),
        "sharp_turn_count": int(row.get("sharp_turn_count", 0)),
        "high_rpm_minutes": float(row.get("high_rpm_minutes", 0.0)),
        "idle_time": float(row.get("idle_time", 0.0)),
        "coolant_overheat": float(row.get("coolant_temp_max", 0.0)) >= 108.0,
        "low_battery": float(row.get("battery_voltage_min", 99.0)) <= 11.8,
        "high_engine_load": float(row.get("engine_load_max", 0.0)) >= 92.0,
    }
    events["has_risky_event"] = any(
        [
            events["hard_accel_count"] >= 5,
            events["hard_brake_count"] >= 5,
            events["sharp_turn_count"] >= 4,
            events["high_rpm_minutes"] >= 8,
            events["coolant_overheat"],
            events["low_battery"],
            events["high_engine_load"],
        ]
    )
    return events
