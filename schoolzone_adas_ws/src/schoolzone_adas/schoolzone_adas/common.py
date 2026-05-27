import json
import math
import time
from typing import Any, Dict, Optional


RISK_STATES = ("SAFE", "CAUTION", "WARNING", "BRAKE")
FEATURE_NAMES = (
    "person_detected",
    "centroid_x",
    "centroid_z",
    "extent_x",
    "extent_y",
    "corridor_overlap_ratio",
    "lateral_velocity_x",
    "approach_velocity_z",
    "ttc",
    "occlusion_flag",
)


def now_payload(**values: Any) -> Dict[str, Any]:
    payload = {"stamp": time.time()}
    payload.update(values)
    return payload


def to_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, allow_nan=False)


def from_json(data: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return {} if default is None else default
    return parsed if isinstance(parsed, dict) else ({} if default is None else default)


def finite_or(value: Any, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    return numeric if math.isfinite(numeric) else default


def feature_vector(features: Dict[str, Any]) -> list:
    vector = []
    for name in FEATURE_NAMES:
        if name in ("person_detected", "occlusion_flag"):
            vector.append(1.0 if features.get(name, False) else 0.0)
        else:
            vector.append(finite_or(features.get(name), 99.0 if name == "ttc" else 0.0))
    return vector


def empty_features() -> Dict[str, Any]:
    return {
        "person_detected": False,
        "centroid_x": 0.0,
        "centroid_z": 0.0,
        "extent_x": 0.0,
        "extent_y": 0.0,
        "corridor_overlap_ratio": 0.0,
        "lateral_velocity_x": 0.0,
        "approach_velocity_z": 0.0,
        "ttc": 99.0,
        "occlusion_flag": False,
    }
