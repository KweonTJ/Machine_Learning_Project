# 합성 데이터 사용 여부 점검

확인일: 2026-06-05

## 결론

현재 프로젝트에는 합성 데이터가 아직 남아 있고, 일부는 최종 실험 결과에도 포함되어 있다.

| 구분 | 현재 사용 여부 | 위치 | 비고 |
| --- | --- | --- | --- |
| 프로젝트 내부 생성 합성 trip 데이터 | 데모 파이프라인에서만 사용 | `src/vehicle_health_report/synthetic.py`, `src/vehicle_health_report/pipeline.py`, `data/processed/simulated_trip_features.csv` | 최종 추가 실험 스크립트에는 포함되지 않지만, `scripts/run_demo.py` 실행 시 생성/사용됨 |
| Vehicle Maintenance Telemetry Data | 최종 추가 실험에 포함 | `data/raw/vehicle_maintenance/archive/synthetic_telemetry_data.csv`, `outputs/vehicle_maintenance_metrics.json` | Kaggle 데이터셋 자체가 합성 차량 telemetry 데이터 |
| AI4I 2020 Predictive Maintenance Dataset | 최종 추가 실험에 포함 | `data/raw/ai4i/ai4i2020.csv`, `outputs/ai4i_metrics.json` | UCI가 synthetic predictive maintenance dataset이라고 명시 |
| Mendeley smartphone sensor | 최종 실험에 포함 | `data/raw/mendeley_phone_sensor/3_FinalDatasetCsv.csv` | 실제 주행 중 스마트폰 센서 데이터 |
| OBD-II/CAN Driving Behavior | 최종 실험에 포함 | `data/raw/obd_can/archive.zip` | 차량 OBD-II/CAN 주행 데이터 |
| KIT Automotive OBD-II | 최종 실험에 포함 | `data/raw/automotive_obd_ii/` | 실제 OBD-II trip 로그 기반 데이터 |

## 코드 기준 확인

### 1. 프로젝트 내부 합성 데이터

`scripts/run_demo.py`는 `vehicle_health_report.cli`를 실행하고, CLI는 `pipeline.run_demo()`를 호출한다.

`pipeline.run_demo()` 내부에서는 다음 흐름으로 합성 데이터를 만든다.

```python
frame = generate_trip_samples(n_samples=samples, random_state=seed)
data_path = processed_dir / "simulated_trip_features.csv"
frame.to_csv(data_path, index=False)
```

즉 `python3 scripts/run_demo.py`를 실행하면 `data/processed/simulated_trip_features.csv`가 생성되고, 이 데이터로 demo 성능 지표와 demo daily report가 만들어진다.

다만 최종 추가 데이터셋 실험 스크립트인 `scripts/run_additional_experiments.py`는 이 합성 trip 데이터를 호출하지 않는다.

### 2. Vehicle Maintenance Telemetry Data

`expanded_experiments.py`는 다음 경로가 존재하면 Vehicle Maintenance 실험을 실행한다.

```text
data/raw/vehicle_maintenance/archive/synthetic_telemetry_data.csv
```

현재 로컬에는 다음 파일이 존재한다.

```text
data/raw/vehicle_maintenance/archive.zip
data/raw/vehicle_maintenance/archive/synthetic_telemetry_data.csv
```

따라서 최종 추가 실험 중 `vehicle_maintenance`는 합성 telemetry 데이터셋을 사용하고 있다.

### 3. AI4I 2020 Predictive Maintenance

`expanded_experiments.py`는 다음 파일이 있으면 AI4I 실험을 실행한다.

```text
data/raw/ai4i/ai4i2020.csv
```

현재 로컬에는 해당 파일이 존재하며, UCI 설명 기준 AI4I 2020은 산업 예지정비 데이터를 반영하도록 만든 synthetic dataset이다.

## 합성 데이터 얻는 방법

### 1. 프로젝트 내부 demo 합성 데이터

외부 다운로드가 필요 없다. 아래 명령으로 로컬에서 생성한다.

```bash
python3 scripts/run_demo.py --samples 800 --seed 42
```

생성 위치:

```text
data/processed/simulated_trip_features.csv
```

### 2. Vehicle Maintenance Telemetry Data

데이터셋 페이지:

```text
https://www.kaggle.com/datasets/tejalaveti2306/vehicle-maintenance-telemetry-data
```

수동 다운로드 방법:

1. Kaggle 계정으로 로그인한다.
2. 위 데이터셋 페이지에서 Download를 누른다.
3. 내려받은 ZIP 파일을 다음 경로에 둔다.

```text
data/raw/vehicle_maintenance/archive.zip
```

4. 실험 실행 시 코드가 ZIP을 풀어 다음 파일을 만든다.

```text
data/raw/vehicle_maintenance/archive/synthetic_telemetry_data.csv
```

Kaggle CLI 사용 방법:

```bash
mkdir -p data/raw/vehicle_maintenance
kaggle datasets download -d tejalaveti2306/vehicle-maintenance-telemetry-data -p data/raw/vehicle_maintenance
mv data/raw/vehicle_maintenance/vehicle-maintenance-telemetry-data.zip data/raw/vehicle_maintenance/archive.zip
python3 scripts/run_additional_experiments.py
```

### 3. AI4I 2020 Predictive Maintenance Dataset

데이터셋 페이지:

```text
https://archive.ics.uci.edu/dataset/601/ai4i
```

직접 다운로드 방법:

```bash
mkdir -p data/raw/ai4i
curl -L "https://cdn.uci-ics-mlr-prod.aws.uci.edu/601/ai4i%2B2020%2Bpredictive%2Bmaintenance%2Bdataset.zip" -o data/raw/ai4i/ai4i2020.zip
unzip data/raw/ai4i/ai4i2020.zip -d data/raw/ai4i
python3 scripts/run_additional_experiments.py
```

UCI Python 패키지 사용 방법:

```python
from ucimlrepo import fetch_ucirepo

ai4i_2020_predictive_maintenance_dataset = fetch_ucirepo(id=601)
X = ai4i_2020_predictive_maintenance_dataset.data.features
y = ai4i_2020_predictive_maintenance_dataset.data.targets
```

## 합성 데이터를 빼고 싶을 때

합성 데이터를 완전히 제외하려면 최종 실험/보고서/PPT에서 다음을 제거하거나 보조 벤치마크로 명확히 표시해야 한다.

- `vehicle_maintenance`
- `ai4i`
- `scripts/run_demo.py` 기반 demo 결과
- `outputs/metrics.json`, `outputs/confusion_matrix.csv`, `outputs/feature_importance.csv`
- `data/processed/simulated_trip_features.csv`
- `reports/demo_daily_report.md`

합성 데이터를 제외한 상태에서 유지 가능한 현재 실험은 다음이다.

- Mendeley smartphone sensor
- OBD-II/CAN Driving Behavior
- KIT Automotive OBD-II

추가 대안으로는 이미 다운로드/확인된 APS Failure at Scania Trucks와 MetroPT-3을 사용할 수 있지만, APS는 feature가 익명화되어 설명력이 낮고 MetroPT-3은 차량 데이터가 아니라 설비 시계열 이상 탐지에 더 가깝다.

## 권장 정리 방식

보고서에는 다음처럼 명확히 쓰는 것이 안전하다.

> 본 프로젝트는 실제 차량/센서 데이터셋인 Mendeley, OBD-II/CAN, KIT OBD-II를 중심으로 주행 습관 분류를 수행했고, Vehicle Maintenance Telemetry와 AI4I는 정비/예지정비 구조를 검증하기 위한 합성 보조 벤치마크로 사용했다.
