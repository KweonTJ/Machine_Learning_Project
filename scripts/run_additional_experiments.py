#!/usr/bin/env python3
"""Run experiments for downloaded additional vehicle datasets."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vehicle_health_report.expanded_experiments import run_all_additional_experiments


def main() -> int:
    results = run_all_additional_experiments(PROJECT_ROOT)
    if not results:
        print("추가 데이터셋을 찾지 못했습니다.")
        return 1

    print("추가 데이터셋 실험 완료")
    for name, result in results.items():
        metrics = result["metrics"]
        print(f"\n[{name}]")
        print(f"- 전처리 데이터: {result['processed_path']}")
        print(f"- 평가 지표: {result['metrics_path']}")
        print(f"- Confusion Matrix: {result['confusion_path']}")
        print(f"- Feature importance: {result['importance_path']}")
        print(f"- 실험 요약: {result['summary_path']}")
        print(f"- Accuracy: {metrics['accuracy']:.3f}")
        print(f"- Macro F1: {metrics['macro_f1']:.3f}")
        print("- 그래프:")
        for figure_name, path in result["figure_paths"].items():
            print(f"  - {figure_name}: {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
