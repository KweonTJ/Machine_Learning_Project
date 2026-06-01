# AI 차량 점검 리포트 시스템

운전자 주행 습관과 차량 상태 데이터를 분석해 일일 차량 점검 리포트를 생성하는 머신러닝 프로젝트입니다. 현재 구현은 PDF 계획서의 핵심 흐름인 `데이터 전처리 -> feature 추출 -> 운전 습관 분류 -> 차량 상태 이상 탐지 -> 점검 권장 -> 리포트 생성`을 바로 실행 가능한 Python 파이프라인으로 구성합니다.

## 현재 구현 범위

- 운전 습관 분류: `normal / aggressive / risky`
- 이벤트 감지: 급가속, 급제동, 급회전, 고RPM, 장시간 정체/공회전
- 차량 상태 분석: RPM, 엔진 부하, 냉각수 온도, 배터리 전압 기반 이상 가능성 추정
- 점검 권장: 브레이크, 타이어, 엔진오일, 배터리, 냉각계 등
- 리포트 생성: 한국어 일일 차량 점검 리포트 Markdown 출력
- 모델 평가: Accuracy, Precision, Recall, F1-score, Confusion Matrix 저장

현재 환경에는 `scikit-learn`이 설치되어 있지 않아 1차 버전은 `numpy/pandas` 기반 자체 baseline 모델로 동작합니다. 실제 제출 단계에서는 `RandomForestClassifier`와 `IsolationForest`로 교체하거나 비교 실험을 추가할 수 있게 구조를 분리했습니다.

## 데이터셋 계획

데이터셋 URL과 접근 방식은 [docs/dataset_sources.md](docs/dataset_sources.md)에 정리했습니다.

UAH-DriveSet은 접근 불가로 보류하고, 1차 구현은 다음 조합을 우선합니다.

- 운전 습관 분석: Mendeley 스마트폰 센서 데이터 + OBD-II/CAN 데이터
- 이벤트 feature 보조: NGSIM 차량 궤적 데이터
- 차량 상태/예지정비: APS Failure at Scania Trucks + Vehicle Maintenance Telemetry Data

실제 데이터 다운로드 전에도 프로젝트 흐름을 검증할 수 있도록 합성 feature 데이터 생성기를 포함했습니다.

## 실행 방법

### 합성 데이터 전체 데모

```bash
python3 scripts/run_demo.py
```

실행 후 생성되는 주요 파일:

- `data/processed/simulated_trip_features.csv`
- `outputs/metrics.json`
- `outputs/confusion_matrix.csv`
- `outputs/feature_importance.csv`
- `reports/demo_daily_report.md`

샘플 수와 난수 시드는 변경할 수 있습니다.

```bash
python3 scripts/run_demo.py --samples 1000 --seed 7
```

### Mendeley 실제 데이터 실험

다운로드한 파일 중 `3_FinalDatasetCsv.csv`를 다음 위치에 둡니다.

```text
data/raw/mendeley_phone_sensor/3_FinalDatasetCsv.csv
```

실험 실행:

```bash
python3 scripts/run_mendeley_experiment.py
```

현재 실제 데이터 실험은 스마트폰 가속도계/자이로스코프 기반 `normal / aggressive` 분류만 수행합니다. 이 데이터셋에는 RPM, 엔진 부하, 냉각수 온도, 배터리 전압이 없으므로 차량 상태 이상 탐지와 점검 권장 리포트는 OBD-II/CAN 또는 정비 데이터와 결합하는 다음 단계에서 확장합니다.

실행 후 생성되는 주요 파일:

- `data/processed/mendeley_sensor_features.csv`
- `outputs/mendeley_metrics.json`
- `outputs/mendeley_confusion_matrix.csv`
- `outputs/mendeley_feature_importance.csv`
- `outputs/figures/mendeley_confusion_matrix.png`
- `outputs/figures/mendeley_feature_importance.png`
- `outputs/figures/mendeley_f1_scores.png`
- `outputs/figures/mendeley_sensor_distribution.png`
- `reports/mendeley_experiment_summary.md`

## 테스트

```bash
python3 -m pytest
```

## 프로젝트 구조

```text
.
├── docs/
│   ├── dataset_sources.md
│   └── project_plan.md
├── scripts/
│   └── run_demo.py
├── src/
│   └── vehicle_health_report/
│       ├── cli.py
│       ├── evaluation.py
│       ├── features.py
│       ├── mendeley.py
│       ├── models.py
│       ├── pipeline.py
│       ├── recommendations.py
│       ├── reporting.py
│       ├── schema.py
│       ├── synthetic.py
│       └── visualization.py
├── tests/
└── reports/
```
