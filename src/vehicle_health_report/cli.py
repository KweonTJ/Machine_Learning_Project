"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI 차량 점검 리포트 데모 실행")
    parser.add_argument("--samples", type=int, default=800, help="생성할 합성 주행 샘플 수")
    parser.add_argument("--seed", type=int, default=42, help="난수 시드")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="출력 파일을 저장할 프로젝트 루트",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_demo(samples=args.samples, seed=args.seed, project_root=args.project_root)
    print("데모 실행 완료")
    print(f"- 데이터: {result['data_path']}")
    print(f"- 평가 지표: {result['metrics_path']}")
    print(f"- Confusion Matrix: {result['confusion_path']}")
    print(f"- Feature importance: {result['importance_path']}")
    print(f"- 리포트: {result['report_path']}")
    print(f"- Accuracy: {result['metrics']['accuracy']:.3f}")
    print(f"- Macro F1: {result['metrics']['macro_f1']:.3f}")
    return 0
