"""Korean Markdown report generation."""

from __future__ import annotations

import pandas as pd

from .features import detect_events
from .schema import STYLE_KO


def build_daily_report(
    row: pd.Series,
    predicted_style: str,
    anomaly_score: float,
    anomaly_flag: int,
    risk_score: int,
    recommendations: list[dict[str, str]],
) -> str:
    events = detect_events(row)
    style_ko = STYLE_KO.get(predicted_style, predicted_style)

    lines = [
        "# 일일 차량 점검 리포트",
        "",
        f"- 주행 ID: `{row['trip_id']}`",
        f"- 총 주행 시간: {row['trip_duration']:.1f}분",
        f"- 운전 습관 등급: {style_ko} (`{predicted_style}`)",
        f"- 위험 운전 점수: {risk_score} / 100",
        f"- 차량 상태 이상 점수: {anomaly_score:.2f}",
        f"- 차량 상태 이상 감지: {'예' if anomaly_flag else '아니오'}",
        "",
        "## 감지된 주행 이벤트",
        "",
        f"- 급가속: {events['hard_accel_count']}회",
        f"- 급제동: {events['hard_brake_count']}회",
        f"- 급회전: {events['sharp_turn_count']}회",
        f"- 고RPM 주행 추정: {events['high_rpm_minutes']:.1f}분",
        f"- 정체/공회전 추정: {events['idle_time']:.1f}분",
        "",
        "## 차량 상태 요약",
        "",
        f"- 평균 RPM: {row['rpm_mean']:.0f} rpm",
        f"- 최대 RPM: {row['rpm_max']:.0f} rpm",
        f"- 최대 엔진 부하: {row['engine_load_max']:.1f}%",
        f"- 최고 냉각수 온도: {row['coolant_temp_max']:.1f}도",
        f"- 최저 배터리 전압: {row['battery_voltage_min']:.2f}V",
        "",
        "## 점검 권장",
        "",
    ]

    for item in recommendations:
        lines.append(
            f"- **{item['component']}** [{item['severity']}]: "
            f"{item['reason']} -> {item['action']}"
        )

    lines.extend(
        [
            "",
            "## 종합 해석",
            "",
            _build_summary(predicted_style, risk_score, anomaly_flag),
            "",
            "> 이 리포트는 센서 데이터 기반 점검 권장 결과이며 실제 고장을 확정하지 않습니다. 반복적으로 위험 신호가 감지되면 정비소 점검이 필요합니다.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_summary(predicted_style: str, risk_score: int, anomaly_flag: int) -> str:
    if risk_score >= 75 or anomaly_flag:
        return "오늘 주행은 차량 부품 부담이 높은 패턴으로 분석되었습니다. 급격한 조작 또는 차량 상태 이상 신호가 관찰되었으므로 관련 부품 점검을 우선 권장합니다."
    if predicted_style == "aggressive" or risk_score >= 50:
        return "오늘은 급가속, 급제동, 급회전 등 차량에 부담을 줄 수 있는 주행 이벤트가 일부 감지되었습니다. 즉시 고장으로 단정할 수는 없지만 반복되면 소모품 점검이 필요합니다."
    return "오늘 주행은 전반적으로 안정적인 패턴으로 분석되었습니다. 특이 이상은 크지 않으나 기본 소모품 점검 주기는 유지하는 것이 좋습니다."
