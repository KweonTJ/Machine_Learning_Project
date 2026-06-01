"""Plotting helpers for experiment outputs."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

import pandas as pd

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
warnings.filterwarnings("ignore", message="Unable to import Axes3D.*")


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def plot_confusion_matrix(matrix: pd.DataFrame, path: Path) -> None:
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    image = ax.imshow(matrix.to_numpy(), cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")

    for row_idx, actual in enumerate(matrix.index):
        for col_idx, predicted in enumerate(matrix.columns):
            ax.text(
                col_idx,
                row_idx,
                str(matrix.loc[actual, predicted]),
                ha="center",
                va="center",
                color="black",
            )

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_feature_importance(importance: pd.Series, path: Path, top_n: int = 10) -> None:
    plt = _pyplot()
    top = importance.sort_values(ascending=True).tail(top_n)
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.barh(top.index, top.values, color="#4C78A8")
    ax.set_xlabel("Relative importance")
    ax.set_title("Top Sensor Features")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_f1_scores(metrics: dict, path: Path) -> None:
    plt = _pyplot()
    labels = list(metrics["labels"].keys())
    scores = [metrics["labels"][label]["f1_score"] for label in labels]
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    ax.bar(labels, scores, color=["#59A14F", "#E15759"][: len(labels)])
    ax.set_ylim(0, 1)
    ax.set_ylabel("F1-score")
    ax.set_title("Class F1 Scores")
    for index, value in enumerate(scores):
        ax.text(index, min(value + 0.025, 0.98), f"{value:.3f}", ha="center")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_sensor_distribution(frame: pd.DataFrame, path: Path) -> None:
    plt = _pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    colors = {"normal": "#59A14F", "aggressive": "#E15759"}
    for label, group in frame.groupby("driving_style"):
        axes[0].hist(
            group["acc_magnitude"],
            bins=45,
            alpha=0.55,
            label=label,
            color=colors.get(label),
            density=True,
        )
        axes[1].hist(
            group["gyro_magnitude"],
            bins=45,
            alpha=0.55,
            label=label,
            color=colors.get(label),
            density=True,
        )
    axes[0].set_title("Acceleration Magnitude")
    axes[1].set_title("Gyroscope Magnitude")
    for ax in axes:
        ax.set_xlabel("Magnitude")
        ax.set_ylabel("Density")
        ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)
