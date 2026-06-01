from vehicle_health_report.pipeline import run_demo


def test_run_demo_creates_outputs(tmp_path):
    result = run_demo(samples=120, seed=11, project_root=tmp_path)

    assert result["data_path"].exists()
    assert result["metrics_path"].exists()
    assert result["confusion_path"].exists()
    assert result["importance_path"].exists()
    assert result["report_path"].exists()
    assert "accuracy" in result["metrics"]
