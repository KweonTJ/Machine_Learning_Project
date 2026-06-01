from pathlib import Path

import pandas as pd

from vehicle_health_report.mendeley import (
    MENDELEY_FEATURES,
    load_mendeley_final_dataset,
    run_mendeley_experiment,
)


def test_load_mendeley_final_dataset_maps_labels(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame(
        {
            "Acc X": [0.1, -0.2],
            "Acc Y": [0.3, 0.4],
            "Acc Z": [0.5, -0.6],
            "gyro_x": [0.01, -0.02],
            "gyro_y": [0.03, 0.04],
            "gyro_z": [0.05, -0.06],
            "label": [0, 1],
        }
    ).to_csv(csv_path, index=False)

    frame = load_mendeley_final_dataset(csv_path)

    assert frame["driving_style"].tolist() == ["normal", "aggressive"]
    for feature in MENDELEY_FEATURES:
        assert feature in frame.columns


def test_run_mendeley_experiment_creates_outputs(tmp_path):
    csv_path = tmp_path / "sample.csv"
    rows = []
    for idx in range(20):
        label = 0 if idx < 10 else 1
        rows.append(
            {
                "Acc X": 0.1 + label * 0.8,
                "Acc Y": 0.2 + label * 0.7,
                "Acc Z": 0.3 + label * 0.6,
                "gyro_x": 0.01 + label * 0.2,
                "gyro_y": 0.02 + label * 0.2,
                "gyro_z": 0.03 + label * 0.2,
                "label": label,
            }
        )
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    result = run_mendeley_experiment(csv_path, Path(tmp_path), test_size=0.25, seed=3)

    assert result["processed_path"].exists()
    assert result["metrics_path"].exists()
    assert result["confusion_path"].exists()
    assert result["importance_path"].exists()
    assert result["summary_path"].exists()
    assert result["metrics"]["dataset"]["rows"] == 20
