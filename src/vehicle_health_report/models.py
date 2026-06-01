"""Lightweight baseline models that run without scikit-learn."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CentroidDrivingStyleClassifier:
    """Nearest standardized class-centroid classifier."""

    feature_names: list[str]

    def fit(self, frame: pd.DataFrame, target: pd.Series) -> "CentroidDrivingStyleClassifier":
        x = frame[self.feature_names].astype(float)
        self.mean_ = x.mean()
        self.std_ = x.std().replace(0, 1.0)
        scaled = (x - self.mean_) / self.std_
        self.labels_ = sorted(target.unique().tolist())
        self.centroids_ = {
            label: scaled.loc[target == label].mean().to_numpy(dtype=float)
            for label in self.labels_
        }
        self.feature_importance_ = self._estimate_feature_importance(scaled, target)
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        scaled = ((frame[self.feature_names].astype(float) - self.mean_) / self.std_).to_numpy()
        predictions = []
        for row in scaled:
            distances = {
                label: float(np.linalg.norm(row - centroid))
                for label, centroid in self.centroids_.items()
            }
            predictions.append(min(distances, key=distances.get))
        return np.array(predictions)

    def _estimate_feature_importance(self, scaled: pd.DataFrame, target: pd.Series) -> pd.Series:
        overall = scaled.mean()
        scores = {}
        for feature in self.feature_names:
            between = 0.0
            for label in sorted(target.unique().tolist()):
                group = scaled.loc[target == label, feature]
                between += len(group) * float((group.mean() - overall[feature]) ** 2)
            total = float(((scaled[feature] - overall[feature]) ** 2).sum()) or 1.0
            scores[feature] = between / total
        result = pd.Series(scores).sort_values(ascending=False)
        return result / (result.sum() or 1.0)


@dataclass
class RobustVehicleAnomalyDetector:
    """Robust z-score anomaly detector for vehicle state features."""

    feature_names: list[str]
    contamination: float = 0.12

    def fit(self, frame: pd.DataFrame) -> "RobustVehicleAnomalyDetector":
        x = frame[self.feature_names].astype(float)
        self.median_ = x.median()
        mad = (x - self.median_).abs().median()
        self.mad_ = mad.replace(0, 1.0)
        train_scores = self.score_samples(frame)
        self.threshold_ = float(np.quantile(train_scores, 1.0 - self.contamination))
        return self

    def score_samples(self, frame: pd.DataFrame) -> np.ndarray:
        x = frame[self.feature_names].astype(float)
        robust_z = ((x - self.median_) / (1.4826 * self.mad_)).abs()
        clipped = np.maximum(robust_z.to_numpy(dtype=float) - 1.5, 0.0)
        return clipped.mean(axis=1)

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        return (self.score_samples(frame) >= self.threshold_).astype(int)


@dataclass
class KNearestNeighborClassifier:
    """Small standardized k-NN classifier for tabular baselines."""

    feature_names: list[str]
    n_neighbors: int = 15
    batch_size: int = 250

    def fit(self, frame: pd.DataFrame, target: pd.Series) -> "KNearestNeighborClassifier":
        x = frame[self.feature_names].astype(float)
        self.mean_ = x.mean().to_numpy(dtype=float)
        self.std_ = x.std().replace(0, 1.0).to_numpy(dtype=float)
        self.x_train_ = ((x.to_numpy(dtype=float) - self.mean_) / self.std_)
        self.y_train_ = target.to_numpy()
        self.labels_ = sorted(target.unique().tolist())
        return self

    def predict(self, frame: pd.DataFrame) -> np.ndarray:
        x = frame[self.feature_names].astype(float).to_numpy(dtype=float)
        x = (x - self.mean_) / self.std_
        predictions = []
        k = min(self.n_neighbors, len(self.x_train_))

        for start in range(0, len(x), self.batch_size):
            batch = x[start : start + self.batch_size]
            distances = ((batch[:, None, :] - self.x_train_[None, :, :]) ** 2).sum(axis=2)
            nearest = np.argpartition(distances, k - 1, axis=1)[:, :k]
            neighbors = self.y_train_[nearest]
            for row in neighbors:
                counts = {label: int((row == label).sum()) for label in self.labels_}
                predictions.append(max(self.labels_, key=lambda label: (counts[label], label)))

        return np.array(predictions)
