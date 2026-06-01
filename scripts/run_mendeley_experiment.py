#!/usr/bin/env python3
"""Run the real Mendeley phone-sensor driving behavior experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vehicle_health_report.mendeley import run_mendeley_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mendeley 운전 습관 분류 실험")
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "mendeley_phone_sensor" / "3_FinalDatasetCsv.csv",
        help="Mendeley 라벨 CSV 경로",
    )
    parser.add_argument("--test-size", type=float, default=0.25, help="테스트 데이터 비율")
    parser.add_argument("--seed", type=int, default=42, help="난수 시드")
    parser.add_argument("--neighbors", type=int, default=15, help="k-NN 이웃 수")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_mendeley_experiment(
        data_path=args.data,
        project_root=PROJECT_ROOT,
        test_size=args.test_size,
        seed=args.seed,
        n_neighbors=args.neighbors,
    )

    print("Mendeley 실제 데이터 실험 완료")
    print(f"- 전처리 데이터: {result['processed_path']}")
    print(f"- 평가 지표: {result['metrics_path']}")
    print(f"- Confusion Matrix: {result['confusion_path']}")
    print(f"- Feature importance: {result['importance_path']}")
    print("- 그래프:")
    for name, path in result["figure_paths"].items():
        print(f"  - {name}: {path}")
    print(f"- 실험 요약: {result['summary_path']}")
    print(f"- Accuracy: {result['metrics']['accuracy']:.3f}")
    print(f"- Macro F1: {result['metrics']['macro_f1']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
