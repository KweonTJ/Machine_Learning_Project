#!/usr/bin/env python3
"""Build the final experiment report HTML from current outputs."""

from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "final_project_report.html"


EXPERIMENTS = [
    {
        "title": "Mendeley 스마트폰 센서",
        "prefix": "mendeley",
        "data_type": "실제 주행 스마트폰 센서",
        "model": "standardized k-NN",
        "task": "normal/aggressive 운전 습관 분류",
        "preprocess": [
            "가속도/자이로 컬럼을 수치형으로 변환하고 결측 행 제거",
            "label 0/1을 normal/aggressive로 매핑",
            "축별 절댓값과 acc/gyro magnitude 파생 feature 생성",
            "라벨 비율을 보존한 75/25 stratified split 적용",
        ],
        "interpretation": "스마트폰 센서만으로 주행 습관을 분류하는 기준선 실험이다. k-NN은 표준화된 센서 feature 공간에서 가까운 학습 샘플의 라벨을 사용해 새 데이터를 분류한다.",
        "figures": [
            ("Confusion Matrix", "outputs/figures/mendeley_confusion_matrix.png"),
            ("Feature Importance", "outputs/figures/mendeley_feature_importance.png"),
            ("F1 Scores", "outputs/figures/mendeley_f1_scores.png"),
            ("Sensor Distribution", "outputs/figures/mendeley_sensor_distribution.png"),
        ],
    },
    {
        "title": "OBD-II/CAN 운전 습관",
        "prefix": "obd_can",
        "data_type": "실제/공개 OBD-II & CAN 차량 내부 신호",
        "model": "standardized class-centroid",
        "task": "moderate/aggressive 운전 습관 분류",
        "preprocess": [
            "스페인어 원본 컬럼명을 프로젝트 표준 feature명으로 매핑",
            "배터리 전압, 엔진 부하, 냉각수 온도, RPM, 속도, throttle 등 수치형 변환",
            "원본 Label 0은 aggressive, Label 1은 moderate로 재정의",
            "라벨 비율을 보존한 75/25 stratified split 적용",
        ],
        "interpretation": "차량 내부 신호 기반 실험이다. 클래스별 평균 벡터를 학습한 뒤 새 데이터가 어느 클래스 중심에 가까운지로 주행 습관을 판정한다.",
        "figures": [
            ("Confusion Matrix", "outputs/figures/obd_can_confusion_matrix.png"),
            ("Feature Importance", "outputs/figures/obd_can_feature_importance.png"),
            ("F1 Scores", "outputs/figures/obd_can_f1_scores.png"),
            ("Feature Distribution", "outputs/figures/obd_can_feature_distribution.png"),
        ],
    },
    {
        "title": "Vehicle Maintenance 이상 탐지",
        "prefix": "vehicle_maintenance",
        "data_type": "Kaggle 공개 차량 telemetry 데이터셋",
        "model": "robust z-score anomaly detector",
        "task": "normal/issue 차량 상태 판정",
        "preprocess": [
            "정비 telemetry 컬럼을 수치형으로 변환하고 필수 feature 결측 제거",
            "failure_type 및 engine/brake/battery issue flag를 issue_label로 통합",
            "정상 데이터만 사용해 median/MAD 기반 정상 범위 학습",
            "테스트 데이터의 robust z-score 평균이 threshold 이상이면 issue로 판정",
        ],
        "interpretation": "Kaggle에서 다운로드한 Vehicle Maintenance Telemetry Data를 사용했다. 정상 차량 상태의 robust 기준을 학습하고, 새 telemetry가 정상 범위를 벗어나는지 보는 이상 탐지 실험이다.",
        "figures": [
            ("Confusion Matrix", "outputs/figures/vehicle_maintenance_confusion_matrix.png"),
            ("Feature Importance", "outputs/figures/vehicle_maintenance_feature_importance.png"),
            ("F1 Scores", "outputs/figures/vehicle_maintenance_f1_scores.png"),
            ("Feature Distribution", "outputs/figures/vehicle_maintenance_feature_distribution.png"),
        ],
        "source_note": "Kaggle 공개 데이터셋이며, 데이터셋 설명상 시뮬레이션 기반 fleet telemetry 성격을 가진다. 본 프로젝트에서 임의 생성한 데이터는 아니다.",
    },
    {
        "title": "KIT Automotive OBD-II",
        "prefix": "automotive_obd_ii",
        "data_type": "실제 OBD-II trip 로그",
        "model": "standardized class-centroid",
        "task": "normal/free_flow/traffic 도로 조건 분류",
        "preprocess": [
            "81개 CSV 주행 로그를 파일 단위 trip으로 집계",
            "파일명에서 Normal/Frei/Stau 라벨을 추출해 road_condition 생성",
            "RPM, 속도, throttle, pedal, 냉각수 온도 등의 mean/max/std/ratio feature 생성",
            "trip 수가 작아 결과 해석 시 데이터 부족을 함께 고려",
        ],
        "interpretation": "row-level OBD 로그를 trip-level feature로 변환하는 검증 실험이다. 데이터 수가 81개로 작아 성능보다 전처리 구조 검증 의미가 크다.",
        "figures": [
            ("Confusion Matrix", "outputs/figures/automotive_obd_ii_confusion_matrix.png"),
            ("Feature Importance", "outputs/figures/automotive_obd_ii_feature_importance.png"),
            ("F1 Scores", "outputs/figures/automotive_obd_ii_f1_scores.png"),
            ("Feature Distribution", "outputs/figures/automotive_obd_ii_feature_distribution.png"),
        ],
    },
    {
        "title": "AI4I 예지정비",
        "prefix": "ai4i",
        "data_type": "UCI 공개 예지정비 벤치마크",
        "model": "standardized class-centroid",
        "task": "normal/failure 고장 여부 분류",
        "preprocess": [
            "온도, 회전 속도, 토크, 마모 feature를 수치형으로 변환",
            "Machine failure 0/1을 normal/failure로 매핑",
            "Type H/L/M을 one-hot feature로 변환",
            "라벨 불균형을 고려해 Accuracy와 Macro F1을 함께 평가",
        ],
        "interpretation": "UCI에서 제공하는 AI4I 2020 Predictive Maintenance Dataset을 사용했다. 차량 직접 데이터는 아니지만 예지정비 문제 구조를 보조 검증하는 공개 benchmark다.",
        "figures": [
            ("Confusion Matrix", "outputs/figures/ai4i_confusion_matrix.png"),
            ("Feature Importance", "outputs/figures/ai4i_feature_importance.png"),
            ("F1 Scores", "outputs/figures/ai4i_f1_scores.png"),
            ("Feature Distribution", "outputs/figures/ai4i_feature_distribution.png"),
        ],
        "source_note": "UCI 공개 벤치마크 데이터셋이며, 산업 예지정비 상황을 반영하도록 설계된 공개 데이터다. 본 프로젝트에서 임의 생성한 데이터는 아니다.",
    },
]


def load_metrics(prefix: str) -> dict:
    return json.loads((PROJECT_ROOT / "outputs" / f"{prefix}_metrics.json").read_text(encoding="utf-8"))


def load_confusion(prefix: str) -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "outputs" / f"{prefix}_confusion_matrix.csv", index_col=0)


def load_importance(prefix: str) -> pd.DataFrame:
    frame = pd.read_csv(PROJECT_ROOT / "outputs" / f"{prefix}_feature_importance.csv")
    return frame.rename(columns={frame.columns[0]: "feature"}).head(5)


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def table(headers: list[str], rows: list[list[object]], class_name: str = "") -> str:
    cls = f' class="{class_name}"' if class_name else ""
    header_html = "".join(f"<th>{e(header)}</th>" for header in headers)
    row_html = []
    for row in rows:
        row_html.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<table{cls}><thead><tr>{header_html}</tr></thead><tbody>{''.join(row_html)}</tbody></table>"


def confusion_table(frame: pd.DataFrame) -> str:
    headers = ["actual \\ predicted", *[str(col) for col in frame.columns]]
    rows: list[list[object]] = []
    for idx, row in frame.iterrows():
        rows.append([f"<strong>{e(idx)}</strong>", *[f"{int(value):,}" for value in row.tolist()]])
    return table(headers, rows, "compact")


def importance_table(frame: pd.DataFrame) -> str:
    rows = [
        [e(row["feature"]), f"{float(row['importance']):.3f}"]
        for _, row in frame.iterrows()
    ]
    return table(["Feature", "Importance"], rows, "compact")


def label_metrics_table(metrics: dict) -> str:
    rows = []
    for label, values in metrics["labels"].items():
        rows.append(
            [
                e(label),
                f"{values['precision']:.3f}",
                f"{values['recall']:.3f}",
                f"{values['f1_score']:.3f}",
                f"{int(values['support']):,}",
            ]
        )
    return table(["Class", "Precision", "Recall", "F1", "Support"], rows, "compact")


def build_summary_rows() -> list[list[object]]:
    rows: list[list[object]] = []
    for item in EXPERIMENTS:
        metrics = load_metrics(item["prefix"])
        confusion = load_confusion(item["prefix"])
        correct = int(confusion.values.diagonal().sum())
        total = int(confusion.values.sum())
        rows.append(
            [
                e(item["title"]),
                e(item["data_type"]),
                e(item["model"]),
                f"{int(metrics['train_rows']):,} / {int(metrics['test_rows']):,}",
                f"{metrics['accuracy']:.3f}",
                f"{metrics['macro_f1']:.3f}",
                f"{correct:,} / {total:,}",
            ]
        )
    return rows


def figure_grid(item: dict) -> str:
    figures = []
    for caption, rel_path in item["figures"]:
        figures.append(
            f"""
            <figure>
              <img src="../{e(rel_path)}" alt="{e(caption)}">
              <figcaption>{e(caption)}</figcaption>
            </figure>
            """
        )
    return '<div class="figure-grid">' + "".join(figures) + "</div>"


def experiment_section(item: dict) -> str:
    metrics = load_metrics(item["prefix"])
    confusion = load_confusion(item["prefix"])
    importance = load_importance(item["prefix"])
    label_counts = metrics.get("dataset", {}).get("label_counts", {})
    label_count_text = ", ".join(f"{label}: {count:,}" for label, count in label_counts.items())
    source_note = ""
    if item.get("source_note"):
        source_note = f'<div class="callout warn"><strong>데이터 출처 및 해석 범위</strong><br>{e(item["source_note"])}</div>'

    preprocess_list = "".join(f"<li>{e(step)}</li>" for step in item["preprocess"])
    threshold = ""
    if "threshold" in metrics:
        threshold = f"<li>이상 탐지 threshold: <strong>{metrics['threshold']:.3f}</strong></li>"

    return f"""
    <section class="experiment page-break">
      <div class="section-kicker">{e(item['prefix'])}</div>
      <h2>{e(item['title'])}</h2>
      <p class="lead">{e(item['interpretation'])}</p>
      {source_note}

      <div class="metric-row">
        <div class="metric-card"><strong>{metrics['accuracy']:.3f}</strong><span>Accuracy</span></div>
        <div class="metric-card"><strong>{metrics['macro_f1']:.3f}</strong><span>Macro F1</span></div>
        <div class="metric-card"><strong>{int(metrics['train_rows']):,}</strong><span>Train rows</span></div>
        <div class="metric-card"><strong>{int(metrics['test_rows']):,}</strong><span>Test rows</span></div>
      </div>

      <div class="two-col">
        <div>
          <h3>데이터와 전처리</h3>
          <ul>
            <li>데이터 성격: <strong>{e(item['data_type'])}</strong></li>
            <li>목표 task: <strong>{e(item['task'])}</strong></li>
            <li>라벨 분포: {e(label_count_text)}</li>
            <li>모델: <strong>{e(item['model'])}</strong></li>
            {threshold}
            {preprocess_list}
          </ul>
        </div>
        <div>
          <h3>Class별 성능</h3>
          {label_metrics_table(metrics)}
        </div>
      </div>

      <div class="two-col">
        <div>
          <h3>Confusion Matrix</h3>
          {confusion_table(confusion)}
        </div>
        <div>
          <h3>Top Feature Importance</h3>
          {importance_table(importance)}
        </div>
      </div>

      <h3>시각적 결과물</h3>
      {figure_grid(item)}
    </section>
    """


def build_html() -> str:
    summary_table = table(
        ["실험", "데이터 성격", "모델", "Train/Test", "Accuracy", "Macro F1", "정답/전체"],
        build_summary_rows(),
    )
    best = max(EXPERIMENTS, key=lambda item: load_metrics(item["prefix"])["macro_f1"])
    best_metrics = load_metrics(best["prefix"])
    experiment_sections = "\n".join(experiment_section(item) for item in EXPERIMENTS)
    figure_count = sum(len(item["figures"]) for item in EXPERIMENTS)

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>AI 차량 점검 리포트 시스템 최종 실험 보고서</title>
  <style>
    @page {{
      size: A4;
      margin: 13mm 12mm 15mm;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      color: #17202a;
      font-family: "Noto Sans CJK KR", "Noto Sans KR", "Malgun Gothic", Arial, sans-serif;
      font-size: 10pt;
      line-height: 1.54;
      background: #ffffff;
    }}
    h1, h2, h3 {{
      margin: 0;
      color: #102a3a;
      line-height: 1.28;
      font-weight: 800;
      letter-spacing: 0;
    }}
    h1 {{
      font-size: 25pt;
    }}
    h2 {{
      margin-top: 14pt;
      padding-bottom: 4pt;
      border-bottom: 1.2pt solid #d9e3ea;
      font-size: 15pt;
    }}
    h3 {{
      margin-top: 11pt;
      margin-bottom: 5pt;
      color: #143445;
      font-size: 11pt;
    }}
    p {{
      margin: 5pt 0;
    }}
    ul {{
      margin: 4pt 0 8pt 16pt;
      padding: 0;
    }}
    li {{
      margin: 2pt 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 6pt 0 10pt;
      table-layout: fixed;
    }}
    th, td {{
      border: 0.8pt solid #d4dee6;
      padding: 4.5pt 5pt;
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
    }}
    th {{
      background: #edf7fb;
      color: #103444;
      font-weight: 800;
    }}
    .compact th, .compact td {{
      padding: 3.8pt 4.5pt;
      font-size: 8.7pt;
    }}
    code {{
      padding: 1pt 3pt;
      border-radius: 3pt;
      background: #f1f5f8;
      font-family: "DejaVu Sans Mono", Consolas, monospace;
      font-size: 8.8pt;
    }}
    .cover {{
      min-height: 249mm;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 9mm 0 6mm;
      page-break-after: always;
    }}
    .eyebrow, .section-kicker {{
      color: #0b7f8c;
      font-size: 9pt;
      font-weight: 800;
      letter-spacing: 0;
    }}
    .subtitle {{
      max-width: 162mm;
      margin-top: 12pt;
      color: #40525d;
      font-size: 12.3pt;
      line-height: 1.55;
    }}
    .meta-grid, .summary-strip, .metric-row {{
      display: grid;
      gap: 7pt;
    }}
    .meta-grid {{
      grid-template-columns: 1fr 1fr;
      margin-top: 20pt;
    }}
    .summary-strip {{
      grid-template-columns: repeat(5, 1fr);
      margin: 14pt 0 8pt;
    }}
    .metric-row {{
      grid-template-columns: repeat(4, 1fr);
      margin: 8pt 0 10pt;
    }}
    .meta-box, .metric-card, .callout {{
      border: 1pt solid #d8e2e8;
      border-left: 4pt solid #14a2b0;
      padding: 8pt 9pt;
      background: #fbfdff;
    }}
    .metric-card strong, .summary-strip strong {{
      display: block;
      color: #0f6f78;
      font-size: 14pt;
      line-height: 1.12;
    }}
    .metric-card span, .summary-strip span, .meta-label {{
      display: block;
      margin-top: 3pt;
      color: #637580;
      font-size: 8.2pt;
      font-weight: 800;
    }}
    .summary-strip .metric-card {{
      min-height: 48pt;
    }}
    .lead {{
      color: #334852;
      font-size: 10.2pt;
    }}
    .callout {{
      margin: 7pt 0 9pt;
      border-left-color: #e17a23;
      background: #fff8ef;
    }}
    .callout.ok {{
      border-left-color: #23975d;
      background: #f3fbf7;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9pt;
      align-items: start;
    }}
    .figure-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8pt;
      margin-top: 6pt;
    }}
    figure {{
      margin: 0;
      break-inside: avoid;
    }}
    figure img {{
      display: block;
      width: 100%;
      max-height: 86mm;
      object-fit: contain;
      border: 0.8pt solid #d6e0e7;
      background: #ffffff;
    }}
    figcaption {{
      margin-top: 3pt;
      color: #52646f;
      font-size: 8.2pt;
      font-weight: 800;
      text-align: center;
    }}
    .page-break {{
      page-break-before: always;
    }}
    .footer-note {{
      color: #60717b;
      font-size: 8.5pt;
    }}
  </style>
</head>
<body>
  <section class="cover">
    <div>
      <div class="eyebrow">최종 실험 결과 기반 보고서</div>
      <h1>AI 차량 점검 리포트 시스템<br>최종 실험 보고서</h1>
      <p class="subtitle">
        차량 센서 데이터와 정비/예지정비 데이터를 대상으로 `데이터 전처리 -> 머신러닝 학습 ->
        새 데이터 적용 -> 결과 도출` 흐름을 재실험하고, 성능 지표와 시각적 결과물을 최종 정리했다.
      </p>

      <div class="meta-grid">
        <div class="meta-box">
          <div class="meta-label">프로젝트 경로</div>
          <strong>{e(PROJECT_ROOT)}</strong>
        </div>
        <div class="meta-box">
          <div class="meta-label">보고서 생성일</div>
          <strong>{date.today().isoformat()}</strong>
        </div>
        <div class="meta-box">
          <div class="meta-label">재실험 명령</div>
          <strong>run_mendeley_experiment.py + run_additional_experiments.py</strong>
        </div>
        <div class="meta-box">
          <div class="meta-label">포함 그래프</div>
          <strong>{figure_count}개 figure</strong>
        </div>
      </div>

      <div class="summary-strip">
        <div class="metric-card"><strong>{load_metrics('obd_can')['macro_f1']:.3f}</strong><span>OBD/CAN Macro F1</span></div>
        <div class="metric-card"><strong>{load_metrics('mendeley')['macro_f1']:.3f}</strong><span>Mendeley Macro F1</span></div>
        <div class="metric-card"><strong>{load_metrics('vehicle_maintenance')['macro_f1']:.3f}</strong><span>Maintenance Macro F1</span></div>
        <div class="metric-card"><strong>{load_metrics('ai4i')['macro_f1']:.3f}</strong><span>AI4I Macro F1</span></div>
        <div class="metric-card"><strong>{load_metrics('automotive_obd_ii')['macro_f1']:.3f}</strong><span>KIT OBD-II Macro F1</span></div>
      </div>

      <div class="callout ok">
        <strong>최종 결론</strong><br>
        가장 안정적인 결과는 {e(best['title'])} 실험이며, Macro F1은 {best_metrics['macro_f1']:.3f}이다.
        실제 차량/센서 데이터 중심 실험은 Mendeley, OBD-II/CAN, KIT Automotive OBD-II이고,
        Vehicle Maintenance는 Kaggle에서 받은 공개 차량 telemetry 데이터셋이고, AI4I는 UCI 공개 예지정비 benchmark다.
        두 데이터셋은 실제 차량/센서 데이터 실험을 보완하는 정비/예지정비 검증 데이터로 해석한다.
      </div>
    </div>
    <p class="footer-note">생성 파일: <code>reports/final_project_report.html</code>, <code>reports/final_project_report.pdf</code></p>
  </section>

  <section>
    <div class="section-kicker">overview</div>
    <h2>1. 프로젝트 개요</h2>
    <p>
      본 프로젝트는 차량 주행 습관과 차량 상태를 분석해 점검 리포트를 만드는 머신러닝 파이프라인이다.
      핵심은 raw 데이터 확보 이후 feature schema를 통일하고, 학습된 기준을 새 데이터에 적용해
      분류 또는 이상 탐지 결과를 산출하는 것이다.
    </p>

    <h3>최종 성능 요약</h3>
    {summary_table}

    <div class="callout">
      <strong>데이터 출처 구분</strong><br>
      Vehicle Maintenance Telemetry는 Kaggle에서 다운로드한 공개 차량 telemetry 데이터셋이고,
      AI4I 2020은 UCI에서 제공하는 공개 예지정비 benchmark다.
      이 둘은 본 프로젝트에서 임의로 만든 데이터가 아니며, 실제 차량/센서 데이터 실험을 보완하는 공개 데이터셋으로 사용했다.
      내부 demo용 `simulated_trip_features.csv`만 프로젝트 코드가 생성한 예시 데이터이며, 최종 추가 실험에는 사용하지 않았다.
    </div>
  </section>

  <section class="page-break">
    <div class="section-kicker">method</div>
    <h2>2. 전처리와 머신러닝 적용 방식</h2>
    <div class="two-col">
      <div>
        <h3>전처리 공통 흐름</h3>
        <ul>
          <li>CSV/ZIP/TAR로 확보한 raw 데이터를 데이터셋별 loader로 읽는다.</li>
          <li>필요 컬럼을 프로젝트 표준 feature명으로 매핑한다.</li>
          <li>센서값을 수치형으로 변환하고 필수 feature와 라벨 결측 행을 제거한다.</li>
          <li>데이터셋별 라벨을 모델 target으로 재정의한다.</li>
          <li>라벨 비율을 보존하는 75/25 stratified split을 적용한다.</li>
          <li>confusion matrix, class별 F1, feature importance, feature distribution을 생성한다.</li>
        </ul>
      </div>
      <div>
        <h3>머신러닝 알고리즘 사용 지점</h3>
        <ul>
          <li><strong>standardized k-NN</strong>: Mendeley 센서 행을 표준화한 뒤 가까운 학습 샘플 다수결로 운전 습관을 분류한다.</li>
          <li><strong>standardized class-centroid</strong>: 클래스별 평균 feature 벡터를 학습하고, 새 데이터가 가장 가까운 클래스 중심으로 분류된다.</li>
          <li><strong>robust z-score anomaly detector</strong>: 정상 정비 telemetry의 median/MAD 기준을 학습하고 정상 범위 이탈을 issue로 판정한다.</li>
          <li><strong>feature importance</strong>: 클래스 간 분산 비율을 기반으로 어떤 feature가 라벨 구분에 중요한지 해석한다.</li>
        </ul>
      </div>
    </div>
  </section>

  {experiment_sections}

  <section class="page-break">
    <div class="section-kicker">conclusion</div>
    <h2>8. 최종 결론과 한계</h2>
    <h3>결론</h3>
    <ul>
      <li>OBD-II/CAN 실험은 Macro F1 {load_metrics('obd_can')['macro_f1']:.3f}로 가장 안정적인 실제 차량 내부 신호 기반 분류 결과를 보였다.</li>
      <li>Mendeley 실험은 스마트폰 센서만으로도 Macro F1 {load_metrics('mendeley')['macro_f1']:.3f}의 주행 습관 분류 기준선을 제공했다.</li>
      <li>Vehicle Maintenance 실험은 Kaggle 공개 telemetry 데이터셋으로 issue를 놓치지 않는 이상 탐지 구조를 보여줬다.</li>
      <li>KIT Automotive OBD-II는 실제 trip 로그 기반이지만 trip 수가 81개로 작아 추가 데이터 확보가 필요하다.</li>
      <li>AI4I는 UCI 공개 예지정비 benchmark이며, failure class 불균형 때문에 Macro F1이 낮게 나타났다.</li>
    </ul>

    <h3>다음 단계</h3>
    <ul>
      <li>정비/고장 예측 파트는 실제 차량 정비 이력 또는 실제 fleet telemetry 데이터로 교체한다.</li>
      <li>KIT OBD-II는 trip 수를 늘리거나 다른 실제 OBD-II 데이터셋을 추가해 다중 클래스 분류 성능을 재평가한다.</li>
      <li>현재 baseline 모델에 RandomForest, Gradient Boosting, IsolationForest 등 비교 모델을 추가한다.</li>
      <li>시계열 특성이 강한 데이터에는 window 기반 feature 또는 sequence 모델을 별도 실험한다.</li>
    </ul>
  </section>
</body>
</html>
"""


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_html(), encoding="utf-8")
    print(f"created: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
