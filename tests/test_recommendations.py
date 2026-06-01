import pandas as pd

from vehicle_health_report.recommendations import build_recommendations, calculate_risk_score


def test_recommendations_include_brake_and_battery_items():
    row = pd.Series(
        {
            "hard_accel_count": 5,
            "hard_brake_count": 4,
            "sharp_turn_count": 1,
            "high_rpm_minutes": 3.0,
            "idle_time": 4.0,
            "coolant_temp_max": 94.0,
            "battery_voltage_min": 11.4,
            "engine_load_max": 74.0,
        }
    )

    items = build_recommendations(row, "aggressive", anomaly_score=0.8, anomaly_flag=1)
    components = {item["component"] for item in items}

    assert "브레이크" in components
    assert "배터리" in components
    assert "종합 점검" in components


def test_risk_score_is_bounded():
    row = pd.Series(
        {
            "hard_accel_count": 20,
            "hard_brake_count": 20,
            "sharp_turn_count": 10,
        }
    )

    score = calculate_risk_score(row, "risky", anomaly_score=5.0, anomaly_flag=1)

    assert 0 <= score <= 100
    assert score == 100
