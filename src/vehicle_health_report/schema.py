"""Shared feature names and project constants."""

DRIVING_FEATURES = [
    "speed_mean",
    "speed_max",
    "acceleration_mean",
    "acceleration_max",
    "brake_intensity_mean",
    "brake_intensity_max",
    "jerk_mean",
    "jerk_max",
    "yaw_rate_mean",
    "yaw_rate_max",
    "trip_duration",
    "hard_accel_count",
    "hard_brake_count",
    "sharp_turn_count",
    "idle_time",
]

VEHICLE_FEATURES = [
    "rpm_mean",
    "rpm_max",
    "engine_load_mean",
    "engine_load_max",
    "coolant_temp_mean",
    "coolant_temp_max",
    "battery_voltage_mean",
    "battery_voltage_min",
    "high_rpm_minutes",
]

MODEL_FEATURES = DRIVING_FEATURES + VEHICLE_FEATURES

STYLE_LABELS = ["normal", "aggressive", "risky"]

STYLE_KO = {
    "normal": "정상",
    "aggressive": "주의",
    "risky": "위험",
}
