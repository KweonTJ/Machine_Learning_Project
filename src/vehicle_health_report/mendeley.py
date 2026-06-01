"""Loader and experiment pipeline for the Mendeley phone sensor dataset."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .evaluation import classification_report_dict, confusion_matrix_frame, write_json
from .models import CentroidDrivingStyleClassifier, KNearestNeighborClassifier
from .visualization import (
    plot_confusion_matrix,
    plot_f1_scores,
    plot_feature_importance,
    plot_sensor_distribution,
)

RAW_COLUMNS = ["Acc X", "Acc Y", "Acc Z", "gyro_x", "gyro_y", "gyro_z"]

MENDELEY_FEATURES = [
    "acc_x",
    "acc_y",
    "acc_z",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "acc_abs_x",
    "acc_abs_y",
    "acc_abs_z",
    "gyro_abs_x",
    "gyro_abs_y",
    "gyro_abs_z",
    "acc_magnitude",
    "gyro_magnitude",
]

MENDELEY_LABELS = ["normal", "aggressive"]


def load_mendeley_final_dataset(path: Path) -> pd.DataFrame:
    """Load the labeled final CSV and normalize column names/labels."""

    raw = pd.read_csv(path)
    missing = [column for column in [*RAW_COLUMNS, "label"] if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing required Mendeley columns: {missing}")

    frame = pd.DataFrame(
        {
            "acc_x": pd.to_numeric(raw["Acc X"], errors="coerce"),
            "acc_y": pd.to_numeric(raw["Acc Y"], errors="coerce"),
            "acc_z": pd.to_numeric(raw["Acc Z"], errors="coerce"),
            "gyro_x": pd.to_numeric(raw["gyro_x"], errors="coerce"),
            "gyro_y": pd.to_numeric(raw["gyro_y"], errors="coerce"),
            "gyro_z": pd.to_numeric(raw["gyro_z"], errors="coerce"),
            "label": raw["label"],
        }
    )
    frame = frame.dropna().reset_index(drop=True)
    frame["driving_style"] = frame["label"].map({0: "normal", 1: "aggressive"})
    if frame["driving_style"].isna().any():
        bad_labels = sorted(frame.loc[frame["driving_style"].isna(), "label"].unique().tolist())
        raise ValueError(f"Unknown Mendeley labels: {bad_labels}")

    return add_sensor_features(frame)


def add_sensor_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add derived phone-sensor features used by the classifier."""

    result = frame.copy()
    for axis in ["x", "y", "z"]:
        result[f"acc_abs_{axis}"] = result[f"acc_{axis}"].abs()
        result[f"gyro_abs_{axis}"] = result[f"gyro_{axis}"].abs()

    result["acc_magnitude"] = np.sqrt(
        result["acc_x"] ** 2 + result["acc_y"] ** 2 + result["acc_z"] ** 2
    )
    result["gyro_magnitude"] = np.sqrt(
        result["gyro_x"] ** 2 + result["gyro_y"] ** 2 + result["gyro_z"] ** 2
    )
    return result


def stratified_split(
    frame: pd.DataFrame,
    target_column: str,
    test_size: float = 0.25,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deterministic stratified split without sklearn."""

    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    train_parts = []
    test_parts = []
    for _, group in frame.groupby(target_column):
        shuffled = group.sample(frac=1.0, random_state=random_state)
        test_count = max(1, int(len(shuffled) * test_size))
        test_parts.append(shuffled.iloc[:test_count])
        train_parts.append(shuffled.iloc[test_count:])

    train = pd.concat(train_parts).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    test = pd.concat(test_parts).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return train, test


def summarize_dataset(frame: pd.DataFrame) -> dict:
    label_counts = frame["driving_style"].value_counts().reindex(MENDELEY_LABELS, fill_value=0)
    return {
        "rows": int(len(frame)),
        "features": MENDELEY_FEATURES,
        "label_counts": {label: int(count) for label, count in label_counts.items()},
    }


def run_mendeley_experiment(
    data_path: Path,
    project_root: Path,
    test_size: float = 0.25,
    seed: int = 42,
    n_neighbors: int = 15,
) -> dict[str, Path | dict]:
    frame = load_mendeley_final_dataset(data_path)
    train, test = stratified_split(frame, "driving_style", test_size=test_size, random_state=seed)

    model = KNearestNeighborClassifier(MENDELEY_FEATURES, n_neighbors=n_neighbors).fit(
        train[MENDELEY_FEATURES],
        train["driving_style"],
    )
    importance_model = CentroidDrivingStyleClassifier(MENDELEY_FEATURES).fit(
        train[MENDELEY_FEATURES],
        train["driving_style"],
    )
    predictions = model.predict(test[MENDELEY_FEATURES])

    metrics = classification_report_dict(test["driving_style"], predictions, MENDELEY_LABELS)
    metrics["dataset"] = summarize_dataset(frame)
    metrics["train_rows"] = int(len(train))
    metrics["test_rows"] = int(len(test))
    metrics["test_size"] = float(test_size)
    metrics["seed"] = int(seed)
    metrics["model"] = {
        "name": "standardized_k_nearest_neighbors",
        "n_neighbors": int(n_neighbors),
    }

    processed_dir = project_root / "data" / "processed"
    outputs_dir = project_root / "outputs"
    figures_dir = outputs_dir / "figures"
    reports_dir = project_root / "reports"
    for directory in [processed_dir, outputs_dir, figures_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    processed_path = processed_dir / "mendeley_sensor_features.csv"
    frame[["driving_style", *MENDELEY_FEATURES]].to_csv(processed_path, index=False)

    metrics_path = outputs_dir / "mendeley_metrics.json"
    write_json(metrics_path, metrics)

    confusion_path = outputs_dir / "mendeley_confusion_matrix.csv"
    confusion = confusion_matrix_frame(test["driving_style"], predictions, MENDELEY_LABELS)
    confusion.to_csv(confusion_path)

    importance_path = outputs_dir / "mendeley_feature_importance.csv"
    importance = importance_model.feature_importance_
    importance.rename("importance").to_csv(importance_path, header=True)

    confusion_plot_path = figures_dir / "mendeley_confusion_matrix.png"
    importance_plot_path = figures_dir / "mendeley_feature_importance.png"
    f1_plot_path = figures_dir / "mendeley_f1_scores.png"
    sensor_plot_path = figures_dir / "mendeley_sensor_distribution.png"
    plot_confusion_matrix(confusion, confusion_plot_path)
    plot_feature_importance(importance, importance_plot_path)
    plot_f1_scores(metrics, f1_plot_path)
    plot_sensor_distribution(frame, sensor_plot_path)

    figure_paths = {
        "confusion_matrix": confusion_plot_path,
        "feature_importance": importance_plot_path,
        "f1_scores": f1_plot_path,
        "sensor_distribution": sensor_plot_path,
    }

    summary_path = reports_dir / "mendeley_experiment_summary.md"
    summary_path.write_text(
        build_experiment_summary(
            metrics,
            _report_relative_path(confusion_path, project_root),
            _report_relative_path(importance_path, project_root),
            {
                name: _report_relative_path(path, project_root)
                for name, path in figure_paths.items()
            },
        ),
        encoding="utf-8",
    )

    return {
        "processed_path": processed_path,
        "metrics_path": metrics_path,
        "confusion_path": confusion_path,
        "importance_path": importance_path,
        "figure_paths": figure_paths,
        "summary_path": summary_path,
        "metrics": metrics,
    }


def _report_relative_path(path: Path, project_root: Path) -> Path:
    return Path("..") / path.relative_to(project_root)


def build_experiment_summary(
    metrics: dict,
    confusion_path: Path,
    importance_path: Path,
    figure_paths: dict[str, Path],
) -> str:
    label_lines = []
    for label in MENDELEY_LABELS:
        values = metrics["labels"][label]
        label_lines.append(
            f"| {label} | {values['precision']:.3f} | {values['recall']:.3f} | "
            f"{values['f1_score']:.3f} | {values['support']} |"
        )

    return "\n".join(
        [
            "# Mendeley 운전 습관 분류 실험 결과",
            "",
            "## 데이터",
            "",
            f"- 전체 행 수: {metrics['dataset']['rows']}",
            f"- 학습 행 수: {metrics['train_rows']}",
            f"- 테스트 행 수: {metrics['test_rows']}",
            f"- 라벨 분포: normal {metrics['dataset']['label_counts']['normal']}개, "
            f"aggressive {metrics['dataset']['label_counts']['aggressive']}개",
            f"- 모델: standardized k-NN, k={metrics['model']['n_neighbors']}",
            "",
            "## 성능",
            "",
            f"- Accuracy: {metrics['accuracy']:.3f}",
            f"- Macro F1: {metrics['macro_f1']:.3f}",
            "",
            "| Class | Precision | Recall | F1-score | Support |",
            "| --- | ---: | ---: | ---: | ---: |",
            *label_lines,
            "",
            "## 산출 파일",
            "",
            f"- Confusion Matrix: `{confusion_path}`",
            f"- Feature importance: `{importance_path}`",
            "",
            "## 시각화",
            "",
            f"![Confusion Matrix]({figure_paths['confusion_matrix']})",
            "",
            f"![Feature Importance]({figure_paths['feature_importance']})",
            "",
            f"![Class F1 Scores]({figure_paths['f1_scores']})",
            "",
            f"![Sensor Distribution]({figure_paths['sensor_distribution']})",
            "",
            "## 해석",
            "",
            "이 실험은 스마트폰 가속도계와 자이로스코프 데이터만 사용해 normal/aggressive 운전 습관을 분류한다. "
            "차량 RPM, 엔진 부하, 냉각수 온도, 배터리 전압은 이 데이터셋에 없으므로 차량 상태 이상 탐지와 점검 권장 리포트는 별도 OBD-II/CAN 또는 정비 데이터와 결합해야 한다.",
            "",
        ]
    )
