"""End-to-end demo pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .evaluation import classification_report_dict, confusion_matrix_frame, write_json
from .models import CentroidDrivingStyleClassifier, RobustVehicleAnomalyDetector
from .recommendations import build_recommendations, calculate_risk_score
from .reporting import build_daily_report
from .schema import MODEL_FEATURES, STYLE_LABELS, VEHICLE_FEATURES
from .synthetic import generate_trip_samples, train_test_split


def run_demo(
    samples: int = 800,
    seed: int = 42,
    project_root: Path | None = None,
) -> dict[str, Path | dict]:
    root = project_root or Path.cwd()
    processed_dir = root / "data" / "processed"
    outputs_dir = root / "outputs"
    reports_dir = root / "reports"
    for directory in [processed_dir, outputs_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    frame = generate_trip_samples(n_samples=samples, random_state=seed)
    data_path = processed_dir / "simulated_trip_features.csv"
    frame.to_csv(data_path, index=False)

    train, test = train_test_split(frame, test_size=0.25, random_state=seed)

    style_model = CentroidDrivingStyleClassifier(MODEL_FEATURES).fit(
        train[MODEL_FEATURES],
        train["driving_style"],
    )
    predictions = style_model.predict(test[MODEL_FEATURES])
    metrics = classification_report_dict(test["driving_style"], predictions, STYLE_LABELS)
    metrics_path = outputs_dir / "metrics.json"
    write_json(metrics_path, metrics)

    confusion = confusion_matrix_frame(test["driving_style"], predictions, STYLE_LABELS)
    confusion_path = outputs_dir / "confusion_matrix.csv"
    confusion.to_csv(confusion_path)

    importance_path = outputs_dir / "feature_importance.csv"
    style_model.feature_importance_.rename("importance").to_csv(importance_path, header=True)

    normal_train = train.loc[train["driving_style"] == "normal", VEHICLE_FEATURES]
    anomaly_model = RobustVehicleAnomalyDetector(VEHICLE_FEATURES).fit(normal_train)

    demo_row = _choose_demo_trip(test, predictions)
    demo_frame = pd.DataFrame([demo_row])
    predicted_style = str(style_model.predict(demo_frame[MODEL_FEATURES])[0])
    anomaly_score = float(anomaly_model.score_samples(demo_frame[VEHICLE_FEATURES])[0])
    anomaly_flag = int(anomaly_model.predict(demo_frame[VEHICLE_FEATURES])[0])
    risk_score = calculate_risk_score(demo_row, predicted_style, anomaly_score, anomaly_flag)
    recommendations = build_recommendations(
        demo_row,
        predicted_style,
        anomaly_score,
        anomaly_flag,
    )
    report = build_daily_report(
        demo_row,
        predicted_style,
        anomaly_score,
        anomaly_flag,
        risk_score,
        recommendations,
    )
    report_path = reports_dir / "demo_daily_report.md"
    report_path.write_text(report, encoding="utf-8")

    return {
        "data_path": data_path,
        "metrics_path": metrics_path,
        "confusion_path": confusion_path,
        "importance_path": importance_path,
        "report_path": report_path,
        "metrics": metrics,
    }


def _choose_demo_trip(test: pd.DataFrame, predictions) -> pd.Series:
    scored = test.copy()
    scored["predicted_style"] = predictions
    risky = scored.loc[scored["predicted_style"].isin(["risky", "aggressive"])]
    if len(risky):
        sort_cols = ["vehicle_anomaly_label", "hard_brake_count", "hard_accel_count"]
        return risky.sort_values(sort_cols, ascending=False).iloc[0]
    return scored.iloc[0]
