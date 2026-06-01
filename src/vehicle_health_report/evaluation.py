"""Model evaluation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def classification_report_dict(
    y_true: pd.Series | np.ndarray,
    y_pred: pd.Series | np.ndarray,
    labels: list[str],
) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    report: dict[str, object] = {
        "accuracy": float((y_true == y_pred).mean()),
        "labels": {},
    }

    f1_values = []
    for label in labels:
        tp = int(((y_true == label) & (y_pred == label)).sum())
        fp = int(((y_true != label) & (y_pred == label)).sum())
        fn = int(((y_true == label) & (y_pred != label)).sum())
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        f1_values.append(f1)
        report["labels"][label] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "support": int((y_true == label).sum()),
        }

    report["macro_f1"] = float(np.mean(f1_values))
    return report


def confusion_matrix_frame(
    y_true: pd.Series | np.ndarray,
    y_pred: pd.Series | np.ndarray,
    labels: list[str],
) -> pd.DataFrame:
    matrix = pd.DataFrame(0, index=labels, columns=labels, dtype=int)
    for actual, predicted in zip(y_true, y_pred):
        matrix.loc[actual, predicted] += 1
    matrix.index.name = "actual"
    matrix.columns.name = "predicted"
    return matrix


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
