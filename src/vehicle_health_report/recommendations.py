"""Rule-based inspection recommendations."""

from __future__ import annotations

import pandas as pd

from .features import detect_events


def calculate_risk_score(
    row: pd.Series,
    predicted_style: str,
    anomaly_score: float,
    anomaly_flag: int,
) -> int:
    style_base = {"normal": 18, "aggressive": 48, "risky": 68}.get(predicted_style, 35)
    event_score = min(
        24,
        int(row["hard_accel_count"] * 2.0)
        + int(row["hard_brake_count"] * 2.2)
        + int(row["sharp_turn_count"] * 2.0),
    )
    vehicle_score = min(20, int(anomaly_score * 18) + (10 if anomaly_flag else 0))
    return int(max(0, min(100, style_base + event_score + vehicle_score)))


def build_recommendations(
    row: pd.Series,
    predicted_style: str,
    anomaly_score: float,
    anomaly_flag: int,
) -> list[dict[str, str]]:
    events = detect_events(row)
    recommendations: list[dict[str, str]] = []

    def add(component: str, reason: str, action: str, severity: str) -> None:
        recommendations.append(
            {
                "component": component,
                "reason": reason,
                "action": action,
                "severity": severity,
            }
        )

    if events["hard_brake_count"] >= 3:
        add(
            "브레이크",
            f"급제동 {events['hard_brake_count']}회 감지",
            "브레이크 패드 마모와 제동 소음을 확인",
            "주의",
        )
    if events["hard_accel_count"] >= 4:
        add(
            "엔진/변속기",
            f"급가속 {events['hard_accel_count']}회 감지",
            "엔진오일 상태와 변속 충격 여부 확인",
            "주의",
        )
    if events["sharp_turn_count"] >= 2:
        add(
            "타이어/서스펜션",
            f"급회전 {events['sharp_turn_count']}회 감지",
            "타이어 마모, 공기압, 편마모 여부 확인",
            "주의",
        )
    if events["high_rpm_minutes"] >= 5:
        add(
            "엔진오일/냉각계",
            f"고RPM 주행 {events['high_rpm_minutes']:.1f}분 추정",
            "엔진오일 교환 주기와 냉각수 상태 확인",
            "주의",
        )
    if events["coolant_overheat"]:
        add(
            "냉각계",
            f"최고 냉각수 온도 {row['coolant_temp_max']:.1f}도",
            "냉각수, 라디에이터, 팬 작동 상태 점검",
            "위험",
        )
    if events["low_battery"]:
        add(
            "배터리",
            f"최저 배터리 전압 {row['battery_voltage_min']:.2f}V",
            "배터리 충전 상태와 단자 부식 여부 점검",
            "위험",
        )
    if events["idle_time"] >= 15:
        add(
            "엔진/냉각계",
            f"정체 또는 공회전 {events['idle_time']:.1f}분",
            "장시간 공회전 후 엔진 열부하와 냉각 상태 확인",
            "관찰",
        )
    if anomaly_flag:
        add(
            "종합 점검",
            f"차량 상태 이상 점수 {anomaly_score:.2f}",
            "반복 감지 시 정비소에서 OBD-II 진단 권장",
            "주의",
        )
    if predicted_style == "normal" and not recommendations:
        add(
            "정기 점검",
            "특이 주행 이벤트와 차량 상태 이상이 크게 감지되지 않음",
            "타이어 공기압, 엔진오일, 배터리 전압을 정기 주기로 확인",
            "정상",
        )

    return recommendations
