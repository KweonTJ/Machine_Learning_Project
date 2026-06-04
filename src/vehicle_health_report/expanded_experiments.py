"""Experiments for the additional vehicle datasets."""

from __future__ import annotations

from io import StringIO, TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from .evaluation import classification_report_dict, confusion_matrix_frame, write_json
from .mendeley import stratified_split
from .models import CentroidDrivingStyleClassifier, RobustVehicleAnomalyDetector
from .visualization import (
    plot_confusion_matrix,
    plot_f1_scores,
    plot_feature_distribution_by_label,
    plot_feature_importance,
)

OBD_CAN_ARCHIVE_MEMBER = "OBD-II Driving Data - Classified.csv"
OBD_CAN_LABELS = ["moderate", "aggressive"]
OBD_CAN_FEATURES = [
    "battery_voltage",
    "engine_load",
    "coolant_temp",
    "intake_pressure",
    "rpm",
    "speed",
    "throttle_position",
    "relative_throttle_position",
    "accelerator_pedal_d",
    "accelerator_pedal_e",
    "steering_angle",
    "steering_angle_speed",
]

VEHICLE_MAINTENANCE_LABELS = ["normal", "issue"]
VEHICLE_MAINTENANCE_FEATURES = [
    "odometer_reading",
    "engine_temp_c",
    "engine_rpm",
    "oil_pressure_psi",
    "coolant_temp_c",
    "engine_load_percent",
    "throttle_pos_percent",
    "air_flow_rate_gps",
    "exhaust_gas_temp_c",
    "vibration_level",
    "engine_hours",
    "brake_fluid_level_psi",
    "brake_pad_wear_mm",
    "brake_temp_c",
    "abs_fault_indicator",
    "brake_pedal_pos_percent",
    "battery_voltage_v",
    "battery_current_a",
    "battery_temp_c",
    "alternator_output_v",
    "battery_charge_percent",
    "battery_health_percent",
    "vehicle_speed_kph",
]

AUTOMOTIVE_OBD_LABELS = ["normal", "free_flow", "traffic"]
AUTOMOTIVE_OBD_FEATURES = [
    "coolant_temp_mean",
    "coolant_temp_max",
    "intake_pressure_mean",
    "intake_pressure_max",
    "rpm_mean",
    "rpm_max",
    "rpm_std",
    "speed_mean",
    "speed_max",
    "speed_std",
    "air_flow_mean",
    "air_flow_max",
    "throttle_mean",
    "throttle_max",
    "pedal_d_mean",
    "pedal_d_max",
    "pedal_e_mean",
    "pedal_e_max",
    "idle_ratio",
    "high_rpm_ratio",
]

AI4I_LABELS = ["normal", "failure"]
AI4I_FEATURES = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "type_h",
    "type_l",
    "type_m",
]


def run_all_additional_experiments(project_root: Path) -> dict[str, dict]:
    """Run every additional experiment whose raw data is present."""

    results: dict[str, dict] = {}

    obd_can_path = project_root / "data" / "raw" / "obd_can" / "archive.zip"
    if obd_can_path.exists():
        results["obd_can"] = run_obd_can_experiment(obd_can_path, project_root)

    vehicle_maintenance_path = (
        project_root
        / "data"
        / "raw"
        / "vehicle_maintenance"
        / "archive"
        / "synthetic_telemetry_data.csv"
    )
    if not vehicle_maintenance_path.exists():
        vehicle_maintenance_zip = project_root / "data" / "raw" / "vehicle_maintenance" / "archive.zip"
        if vehicle_maintenance_zip.exists():
            with ZipFile(vehicle_maintenance_zip) as archive:
                archive.extractall(vehicle_maintenance_zip.parent / "archive")
    if vehicle_maintenance_path.exists():
        results["vehicle_maintenance"] = run_vehicle_maintenance_experiment(
            vehicle_maintenance_path,
            project_root,
        )

    automotive_obd_dir = (
        project_root / "data" / "raw" / "automotive_obd_ii" / "dataset" / "OBD-II-Dataset"
    )
    if automotive_obd_dir.exists():
        results["automotive_obd_ii"] = run_automotive_obd_experiment(
            automotive_obd_dir,
            project_root,
        )

    ai4i_path = project_root / "data" / "raw" / "ai4i" / "ai4i2020.csv"
    if ai4i_path.exists():
        results["ai4i"] = run_ai4i_experiment(ai4i_path, project_root)

    return results


def run_obd_can_experiment(
    archive_path: Path,
    project_root: Path,
    test_size: float = 0.25,
    seed: int = 42,
) -> dict[str, Path | dict]:
    frame = load_obd_can_dataset(archive_path)
    train, test = stratified_split(frame, "driving_style", test_size=test_size, random_state=seed)

    model = CentroidDrivingStyleClassifier(OBD_CAN_FEATURES).fit(
        train[OBD_CAN_FEATURES],
        train["driving_style"],
    )
    predictions = model.predict(test[OBD_CAN_FEATURES])
    metrics = classification_report_dict(test["driving_style"], predictions, OBD_CAN_LABELS)
    metrics.update(
        {
            "dataset": _dataset_summary(frame, "driving_style", OBD_CAN_LABELS),
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_size": float(test_size),
            "seed": int(seed),
            "model": {"name": "standardized_class_centroid"},
            "label_note": "Raw Label 0 was mapped to aggressive because it has higher speed, load, RPM, and throttle values; Label 1 was mapped to moderate.",
        }
    )

    paths = _write_classification_outputs(
        project_root,
        prefix="obd_can",
        processed_frame=frame[["driving_style", "conductor_id", *OBD_CAN_FEATURES]],
        metrics=metrics,
        labels=OBD_CAN_LABELS,
        y_true=test["driving_style"],
        y_pred=predictions,
        importance=model.feature_importance_,
        distribution_frame=frame,
        distribution_label="driving_style",
        distribution_features=["engine_load", "speed"],
        distribution_title="OBD/CAN Driving Style Feature Distribution",
        summary=build_obd_can_summary(metrics),
    )
    return {**paths, "metrics": metrics}


def load_obd_can_dataset(archive_path: Path) -> pd.DataFrame:
    with ZipFile(archive_path) as archive:
        with archive.open(OBD_CAN_ARCHIVE_MEMBER) as file:
            raw = pd.read_csv(file, encoding="latin1")

    column_map = {
        "battery_voltage": _find_column(raw.columns, ["voltaje", "bateria"]),
        "engine_load": _find_column(raw.columns, ["carga", "calculada", "motor"]),
        "coolant_temp": _find_column(raw.columns, ["temperatura", "enfriamiento", "motor"]),
        "intake_pressure": _find_column(raw.columns, ["presion", "colector", "admision"]),
        "rpm": _find_column(raw.columns, ["rpm", "motor"]),
        "speed": _find_column(raw.columns, ["velocidad", "km/h"]),
        "throttle_position": _find_column(
            raw.columns,
            ["posicion", "absoluta", "acelerador"],
            excludes=[" b"],
        ),
        "relative_throttle_position": _find_column(
            raw.columns,
            ["posicion", "relativa", "acelerador"],
        ),
        "accelerator_pedal_d": _find_column(raw.columns, ["pedal", "acelerador", "d"]),
        "accelerator_pedal_e": _find_column(raw.columns, ["pedal", "acelerador", "e"]),
        "steering_angle": _find_column(
            raw.columns,
            ["angulo", "giro", "volante"],
            excludes=["velocidad"],
        ),
        "steering_angle_speed": _find_column(
            raw.columns,
            ["velocidad", "angulo", "giro", "volante"],
        ),
    }

    frame = pd.DataFrame(
        {feature: pd.to_numeric(raw[column], errors="coerce") for feature, column in column_map.items()}
    )
    frame["driving_style"] = raw["Label"].map({0: "aggressive", 1: "moderate"})
    frame["conductor_id"] = pd.to_numeric(raw["Conductor_ID"], errors="coerce").astype("Int64")
    return frame.dropna(subset=[*OBD_CAN_FEATURES, "driving_style"]).reset_index(drop=True)


def run_vehicle_maintenance_experiment(
    data_path: Path,
    project_root: Path,
    test_size: float = 0.25,
    seed: int = 42,
) -> dict[str, Path | dict]:
    frame = load_vehicle_maintenance_dataset(data_path)
    train, test = stratified_split(frame, "issue_label", test_size=test_size, random_state=seed)

    normal_train = train.loc[train["issue_label"] == "normal", VEHICLE_MAINTENANCE_FEATURES]
    anomaly_model = RobustVehicleAnomalyDetector(
        VEHICLE_MAINTENANCE_FEATURES,
        contamination=0.02,
    ).fit(normal_train)
    predictions = np.where(
        anomaly_model.predict(test[VEHICLE_MAINTENANCE_FEATURES]) == 1,
        "issue",
        "normal",
    )
    importance_model = CentroidDrivingStyleClassifier(VEHICLE_MAINTENANCE_FEATURES).fit(
        train[VEHICLE_MAINTENANCE_FEATURES],
        train["issue_label"],
    )
    metrics = classification_report_dict(test["issue_label"], predictions, VEHICLE_MAINTENANCE_LABELS)
    metrics.update(
        {
            "dataset": _dataset_summary(frame, "issue_label", VEHICLE_MAINTENANCE_LABELS),
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_size": float(test_size),
            "seed": int(seed),
            "model": {
                "name": "robust_z_score_anomaly_detector",
                "contamination": 0.02,
            },
            "threshold": float(anomaly_model.threshold_),
        }
    )

    paths = _write_classification_outputs(
        project_root,
        prefix="vehicle_maintenance",
        processed_frame=frame[["issue_label", "failure_type", *VEHICLE_MAINTENANCE_FEATURES]],
        metrics=metrics,
        labels=VEHICLE_MAINTENANCE_LABELS,
        y_true=test["issue_label"],
        y_pred=predictions,
        importance=importance_model.feature_importance_,
        distribution_frame=frame,
        distribution_label="issue_label",
        distribution_features=["battery_voltage_v", "brake_temp_c", "coolant_temp_c"],
        distribution_title="Vehicle Maintenance Telemetry Distribution",
        summary=build_vehicle_maintenance_summary(metrics),
    )
    return {**paths, "metrics": metrics}


def load_vehicle_maintenance_dataset(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    frame = raw.copy()
    for feature in VEHICLE_MAINTENANCE_FEATURES:
        frame[feature] = pd.to_numeric(frame[feature], errors="coerce")
    issue_flags = (
        (frame["failure_type"].fillna("No Failure") != "No Failure")
        | (pd.to_numeric(frame["engine_failure_imminent"], errors="coerce").fillna(0) > 0)
        | (pd.to_numeric(frame["brake_issue_imminent"], errors="coerce").fillna(0) > 0)
        | (pd.to_numeric(frame["battery_issue_imminent"], errors="coerce").fillna(0) > 0)
    )
    frame["issue_label"] = np.where(issue_flags, "issue", "normal")
    return frame.dropna(subset=[*VEHICLE_MAINTENANCE_FEATURES, "issue_label"]).reset_index(drop=True)


def run_automotive_obd_experiment(
    dataset_dir: Path,
    project_root: Path,
    test_size: float = 0.25,
    seed: int = 42,
) -> dict[str, Path | dict]:
    frame = load_automotive_obd_dataset(dataset_dir)
    train, test = stratified_split(frame, "road_condition", test_size=test_size, random_state=seed)

    model = CentroidDrivingStyleClassifier(AUTOMOTIVE_OBD_FEATURES).fit(
        train[AUTOMOTIVE_OBD_FEATURES],
        train["road_condition"],
    )
    predictions = model.predict(test[AUTOMOTIVE_OBD_FEATURES])
    metrics = classification_report_dict(test["road_condition"], predictions, AUTOMOTIVE_OBD_LABELS)
    metrics.update(
        {
            "dataset": _dataset_summary(frame, "road_condition", AUTOMOTIVE_OBD_LABELS),
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_size": float(test_size),
            "seed": int(seed),
            "model": {"name": "standardized_class_centroid"},
        }
    )

    paths = _write_classification_outputs(
        project_root,
        prefix="automotive_obd_ii",
        processed_frame=frame[["file_name", "road_condition", *AUTOMOTIVE_OBD_FEATURES]],
        metrics=metrics,
        labels=AUTOMOTIVE_OBD_LABELS,
        y_true=test["road_condition"],
        y_pred=predictions,
        importance=model.feature_importance_,
        distribution_frame=frame,
        distribution_label="road_condition",
        distribution_features=["speed_mean", "rpm_mean"],
        distribution_title="Automotive OBD-II Trip Feature Distribution",
        summary=build_automotive_obd_summary(metrics),
    )
    return {**paths, "metrics": metrics}


def load_automotive_obd_dataset(dataset_dir: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(dataset_dir.glob("*.csv")):
        condition = _road_condition_from_filename(path.name)
        if condition is None:
            continue
        raw = pd.read_csv(path)
        column_map = {
            "coolant_temp": _find_column(raw.columns, ["engine", "coolant", "temperature"]),
            "intake_pressure": _find_column(raw.columns, ["intake", "manifold", "pressure"]),
            "rpm": _find_column(raw.columns, ["engine", "rpm"]),
            "speed": _find_column(raw.columns, ["vehicle", "speed"]),
            "air_flow": _find_column(raw.columns, ["air", "flow", "mass"]),
            "throttle": _find_column(raw.columns, ["absolute", "throttle"]),
            "pedal_d": _find_column(raw.columns, ["accelerator", "pedal", "d"]),
            "pedal_e": _find_column(raw.columns, ["accelerator", "pedal", "e"]),
        }
        numeric = pd.DataFrame(
            {name: pd.to_numeric(raw[column], errors="coerce") for name, column in column_map.items()}
        )
        row = {
            "file_name": path.name,
            "road_condition": condition,
            "coolant_temp_mean": numeric["coolant_temp"].mean(),
            "coolant_temp_max": numeric["coolant_temp"].max(),
            "intake_pressure_mean": numeric["intake_pressure"].mean(),
            "intake_pressure_max": numeric["intake_pressure"].max(),
            "rpm_mean": numeric["rpm"].mean(),
            "rpm_max": numeric["rpm"].max(),
            "rpm_std": numeric["rpm"].std(),
            "speed_mean": numeric["speed"].mean(),
            "speed_max": numeric["speed"].max(),
            "speed_std": numeric["speed"].std(),
            "air_flow_mean": numeric["air_flow"].mean(),
            "air_flow_max": numeric["air_flow"].max(),
            "throttle_mean": numeric["throttle"].mean(),
            "throttle_max": numeric["throttle"].max(),
            "pedal_d_mean": numeric["pedal_d"].mean(),
            "pedal_d_max": numeric["pedal_d"].max(),
            "pedal_e_mean": numeric["pedal_e"].mean(),
            "pedal_e_max": numeric["pedal_e"].max(),
            "idle_ratio": float((numeric["speed"] <= 1).mean()),
            "high_rpm_ratio": float((numeric["rpm"] >= 3000).mean()),
        }
        rows.append(row)

    frame = pd.DataFrame(rows)
    return frame.dropna(subset=[*AUTOMOTIVE_OBD_FEATURES, "road_condition"]).reset_index(drop=True)


def run_ai4i_experiment(
    data_path: Path,
    project_root: Path,
    test_size: float = 0.25,
    seed: int = 42,
) -> dict[str, Path | dict]:
    frame = load_ai4i_dataset(data_path)
    train, test = stratified_split(frame, "failure_label", test_size=test_size, random_state=seed)

    model = CentroidDrivingStyleClassifier(AI4I_FEATURES).fit(
        train[AI4I_FEATURES],
        train["failure_label"],
    )
    predictions = model.predict(test[AI4I_FEATURES])
    metrics = classification_report_dict(test["failure_label"], predictions, AI4I_LABELS)
    metrics.update(
        {
            "dataset": _dataset_summary(frame, "failure_label", AI4I_LABELS),
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_size": float(test_size),
            "seed": int(seed),
            "model": {"name": "standardized_class_centroid"},
        }
    )

    paths = _write_classification_outputs(
        project_root,
        prefix="ai4i",
        processed_frame=frame[["failure_label", *AI4I_FEATURES]],
        metrics=metrics,
        labels=AI4I_LABELS,
        y_true=test["failure_label"],
        y_pred=predictions,
        importance=model.feature_importance_,
        distribution_frame=frame,
        distribution_label="failure_label",
        distribution_features=["rotational_speed_rpm", "torque_nm", "tool_wear_min"],
        distribution_title="AI4I Predictive Maintenance Distribution",
        summary=build_ai4i_summary(metrics),
    )
    return {**paths, "metrics": metrics}


def load_ai4i_dataset(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    frame = pd.DataFrame(
        {
            "air_temperature_k": pd.to_numeric(raw["Air temperature [K]"], errors="coerce"),
            "process_temperature_k": pd.to_numeric(raw["Process temperature [K]"], errors="coerce"),
            "rotational_speed_rpm": pd.to_numeric(raw["Rotational speed [rpm]"], errors="coerce"),
            "torque_nm": pd.to_numeric(raw["Torque [Nm]"], errors="coerce"),
            "tool_wear_min": pd.to_numeric(raw["Tool wear [min]"], errors="coerce"),
            "failure_label": raw["Machine failure"].map({0: "normal", 1: "failure"}),
        }
    )
    type_dummies = pd.get_dummies(raw["Type"].str.lower(), prefix="type")
    for column in ["type_h", "type_l", "type_m"]:
        frame[column] = type_dummies.get(column, 0).astype(float)
    return frame.dropna(subset=[*AI4I_FEATURES, "failure_label"]).reset_index(drop=True)


def read_aps_dataset_from_zip(archive_path: Path, member_name: str) -> pd.DataFrame:
    """Read APS CSV files that contain a license preamble before the header."""

    with ZipFile(archive_path) as archive:
        lines = TextIOWrapper(archive.open(member_name), encoding="latin1").read().splitlines()
    header_idx = next(index for index, line in enumerate(lines) if line.startswith("class,"))
    return pd.read_csv(StringIO("\n".join(lines[header_idx:])), na_values="na")


def build_obd_can_summary(metrics: dict) -> str:
    return _build_summary(
        title="OBD-II/CAN 운전 습관 분류 실험 결과",
        metrics=metrics,
        labels=OBD_CAN_LABELS,
        interpretation=(
            "이 실험은 OBD-II/CAN 차량 내부 신호를 사용해 moderate/aggressive 주행을 분류한다. "
            "Mendeley 스마트폰 센서 실험을 차량 내부 데이터 기반 실험으로 보강한다."
        ),
    )


def build_vehicle_maintenance_summary(metrics: dict) -> str:
    return _build_summary(
        title="Vehicle Maintenance 차량 상태 이상 탐지 실험 결과",
        metrics=metrics,
        labels=VEHICLE_MAINTENANCE_LABELS,
        interpretation=(
            "이 실험은 차량 텔레메트리에서 정상 상태 기준을 학습하고, 새 데이터가 정상 범위를 벗어나는지 "
            "robust z-score 이상 탐지로 판정한다. 고장 라벨이 매우 적어 recall과 precision을 함께 봐야 한다."
        ),
    )


def build_automotive_obd_summary(metrics: dict) -> str:
    return _build_summary(
        title="KIT Automotive OBD-II 주행 조건 분류 실험 결과",
        metrics=metrics,
        labels=AUTOMOTIVE_OBD_LABELS,
        interpretation=(
            "이 실험은 실제 OBD-II 주행 로그를 trip 단위 feature로 집계하고 도로 조건을 분류한다. "
            "차량 내부 신호를 프로젝트의 trip-level feature로 변환하는 검증 실험이다."
        ),
    )


def build_ai4i_summary(metrics: dict) -> str:
    return _build_summary(
        title="AI4I 예지정비 분류 실험 결과",
        metrics=metrics,
        labels=AI4I_LABELS,
        interpretation=(
            "이 실험은 차량 데이터는 아니지만 예지정비 벤치마크로, 회전 속도와 토크, 온도, 마모 feature로 "
            "고장 여부를 분류해 정비 예측 파이프라인을 보조 검증한다."
        ),
    )


def _write_classification_outputs(
    project_root: Path,
    prefix: str,
    processed_frame: pd.DataFrame,
    metrics: dict,
    labels: list[str],
    y_true: pd.Series | np.ndarray,
    y_pred: pd.Series | np.ndarray,
    importance: pd.Series,
    distribution_frame: pd.DataFrame,
    distribution_label: str,
    distribution_features: list[str],
    distribution_title: str,
    summary: str,
) -> dict[str, Path | dict]:
    processed_dir = project_root / "data" / "processed"
    outputs_dir = project_root / "outputs"
    figures_dir = outputs_dir / "figures"
    reports_dir = project_root / "reports"
    for directory in [processed_dir, outputs_dir, figures_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    processed_path = processed_dir / f"{prefix}_features.csv"
    processed_frame.to_csv(processed_path, index=False)

    metrics_path = outputs_dir / f"{prefix}_metrics.json"
    write_json(metrics_path, metrics)

    confusion = confusion_matrix_frame(y_true, y_pred, labels)
    confusion_path = outputs_dir / f"{prefix}_confusion_matrix.csv"
    confusion.to_csv(confusion_path)

    importance_path = outputs_dir / f"{prefix}_feature_importance.csv"
    importance.rename("importance").to_csv(importance_path, header=True)

    confusion_plot_path = figures_dir / f"{prefix}_confusion_matrix.png"
    importance_plot_path = figures_dir / f"{prefix}_feature_importance.png"
    f1_plot_path = figures_dir / f"{prefix}_f1_scores.png"
    distribution_plot_path = figures_dir / f"{prefix}_feature_distribution.png"
    plot_confusion_matrix(confusion, confusion_plot_path)
    plot_feature_importance(importance, importance_plot_path)
    plot_f1_scores(metrics, f1_plot_path)
    plot_feature_distribution_by_label(
        distribution_frame,
        distribution_label,
        distribution_features,
        distribution_plot_path,
        distribution_title,
    )

    summary_path = reports_dir / f"{prefix}_experiment_summary.md"
    figure_paths = {
        "confusion_matrix": confusion_plot_path,
        "feature_importance": importance_plot_path,
        "f1_scores": f1_plot_path,
        "feature_distribution": distribution_plot_path,
    }
    summary_path.write_text(
        summary
        + "\n## 시각화\n\n"
        + "\n\n".join(
            [
                f"![{name}](../{path.relative_to(project_root)})"
                for name, path in figure_paths.items()
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "processed_path": processed_path,
        "metrics_path": metrics_path,
        "confusion_path": confusion_path,
        "importance_path": importance_path,
        "figure_paths": figure_paths,
        "summary_path": summary_path,
    }


def _build_summary(title: str, metrics: dict, labels: list[str], interpretation: str) -> str:
    label_lines = []
    for label in labels:
        values = metrics["labels"][label]
        label_lines.append(
            f"| {label} | {values['precision']:.3f} | {values['recall']:.3f} | "
            f"{values['f1_score']:.3f} | {values['support']} |"
        )

    label_counts = metrics["dataset"]["label_counts"]
    label_count_text = ", ".join(f"{label} {label_counts.get(label, 0)}개" for label in labels)
    return "\n".join(
        [
            f"# {title}",
            "",
            "## 데이터",
            "",
            f"- 전체 행 수: {metrics['dataset']['rows']}",
            f"- 학습 행 수: {metrics['train_rows']}",
            f"- 테스트 행 수: {metrics['test_rows']}",
            f"- 라벨 분포: {label_count_text}",
            f"- 모델: {metrics['model']['name']}",
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
            "## 해석",
            "",
            interpretation,
            "",
        ]
    )


def _dataset_summary(frame: pd.DataFrame, label_column: str, labels: list[str]) -> dict:
    counts = frame[label_column].value_counts().reindex(labels, fill_value=0)
    return {
        "rows": int(len(frame)),
        "label_counts": {label: int(count) for label, count in counts.items()},
    }


def _road_condition_from_filename(name: str) -> str | None:
    if "_Stau" in name:
        return "traffic"
    if "_Frei" in name:
        return "free_flow"
    if "_Normal" in name:
        return "normal"
    return None


def _find_column(
    columns: pd.Index,
    includes: list[str],
    excludes: list[str] | None = None,
) -> str:
    normalized_includes = [_normalize_name(value) for value in includes]
    normalized_excludes = [_normalize_name(value) for value in (excludes or [])]
    for column in columns:
        normalized = _normalize_name(column)
        if all(token in normalized for token in normalized_includes) and not any(
            token in normalized for token in normalized_excludes
        ):
            return str(column)
    raise ValueError(f"Could not find column with tokens: {includes}")


def _normalize_name(value: object) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value))
    return text.encode("ascii", "ignore").decode("ascii").lower()
