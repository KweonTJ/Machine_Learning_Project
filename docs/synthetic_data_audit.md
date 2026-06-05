# 공개 데이터셋과 내부 생성 데이터 구분

확인일: 2026-06-05

## 결론

현재 프로젝트에는 두 종류의 데이터가 섞여 있다.

1. 프로젝트 코드가 직접 생성한 내부 demo용 데이터
2. Kaggle/UCI 등 외부에서 다운로드한 공개 데이터셋

중요한 점은 `Vehicle Maintenance Telemetry Data`와 `AI4I 2020`은 본 프로젝트에서 임의로 만든 데이터가 아니라, 각각 Kaggle과 UCI에서 받은 공개 데이터셋이라는 것이다. 다만 데이터셋 설명상 실제 운행 로그라기보다 시뮬레이션/벤치마크 성격이 있으므로, 보고서에서는 “Kaggle 공개 telemetry 데이터셋”, “UCI 공개 예지정비 벤치마크”처럼 출처를 함께 명시한다.

| 구분 | 현재 사용 여부 | 위치 | 비고 |
| --- | --- | --- | --- |
| 프로젝트 내부 생성 demo trip 데이터 | 데모 파이프라인에서만 사용 | `src/vehicle_health_report/synthetic.py`, `src/vehicle_health_report/pipeline.py`, `data/processed/simulated_trip_features.csv` | 프로젝트 코드가 생성한 예시 데이터. 최종 추가 실험에는 사용하지 않음 |
| Vehicle Maintenance Telemetry Data | 최종 추가 실험에 포함 | `data/raw/vehicle_maintenance/archive/synthetic_telemetry_data.csv`, `outputs/vehicle_maintenance_metrics.json` | Kaggle에서 다운로드한 공개 차량 telemetry 데이터셋. 파일명에 synthetic이 들어가지만 본 프로젝트에서 임의 생성한 데이터는 아님 |
| AI4I 2020 Predictive Maintenance Dataset | 최종 추가 실험에 포함 | `data/raw/ai4i/ai4i2020.csv`, `outputs/ai4i_metrics.json` | UCI 공개 예지정비 벤치마크 데이터셋. 본 프로젝트에서 임의 생성한 데이터는 아님 |
| Mendeley smartphone sensor | 최종 실험에 포함 | `data/raw/mendeley_phone_sensor/3_FinalDatasetCsv.csv` | 실제 주행 중 스마트폰 센서 데이터 |
| OBD-II/CAN Driving Behavior | 최종 실험에 포함 | `data/raw/obd_can/archive.zip` | 차량 OBD-II/CAN 주행 데이터 |
| KIT Automotive OBD-II | 최종 실험에 포함 | `data/raw/automotive_obd_ii/` | 실제 OBD-II trip 로그 기반 데이터 |

## 코드 기준 확인

### 1. 프로젝트 내부 생성 demo 데이터

`scripts/run_demo.py`는 `vehicle_health_report.cli`를 실행하고, CLI는 `pipeline.run_demo()`를 호출한다.

`pipeline.run_demo()` 내부에서는 다음 흐름으로 demo용 예시 데이터를 만든다.

```python
frame = generate_trip_samples(n_samples=samples, random_state=seed)
data_path = processed_dir / "simulated_trip_features.csv"
frame.to_csv(data_path, index=False)
```

즉 `python3 scripts/run_demo.py`를 실행하면 `data/processed/simulated_trip_features.csv`가 생성되고, 이 데이터로 demo 성능 지표와 demo daily report가 만들어진다.

다만 최종 추가 데이터셋 실험 스크립트인 `scripts/run_additional_experiments.py`는 이 내부 생성 demo 데이터를 호출하지 않는다.

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

따라서 최종 추가 실험 중 `vehicle_maintenance`는 Kaggle에서 다운로드한 공개 Vehicle Maintenance Telemetry Data를 사용하고 있다. 파일명은 `synthetic_telemetry_data.csv`지만, 이는 데이터셋 원본 파일명이며 본 프로젝트에서 임의로 만든 데이터라는 뜻은 아니다.

### 3. AI4I 2020 Predictive Maintenance

`expanded_experiments.py`는 다음 파일이 있으면 AI4I 실험을 실행한다.

```text
data/raw/ai4i/ai4i2020.csv
```

현재 로컬에는 해당 파일이 존재한다. AI4I 2020은 UCI에서 제공하는 공개 예지정비 benchmark로, 본 프로젝트에서 임의 생성한 데이터가 아니다.

## 데이터 얻는 방법

### 1. 프로젝트 내부 demo 데이터

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

## 보고서 표현 권장

보고서와 발표자료에는 다음처럼 표현하는 것이 좋다.

| 피해야 할 표현 | 권장 표현 |
| --- | --- |
| 합성 데이터를 사용했다 | Kaggle 공개 Vehicle Maintenance Telemetry Data를 사용했다 |
| 합성 telemetry 데이터 | Kaggle 공개 차량 telemetry 데이터셋 |
| 합성 예지정비 데이터 | UCI 공개 AI4I 예지정비 benchmark |
| 내가 만든 데이터 | 공개 데이터셋을 다운로드해 전처리했다 |

내부 demo 데이터는 별도로 다음처럼 표현한다.

> `scripts/run_demo.py`는 프로젝트 흐름 검증용 내부 생성 demo 데이터를 만들지만, 최종 추가 실험 결과에는 사용하지 않았다.

## 공개 benchmark를 빼고 싶을 때

Vehicle Maintenance와 AI4I를 최종 실험/보고서/PPT에서 제외하려면 다음을 제거하거나 “공개 benchmark”로 명확히 표시해야 한다.

- `vehicle_maintenance`
- `ai4i`
- `scripts/run_demo.py` 기반 demo 결과
- `outputs/metrics.json`, `outputs/confusion_matrix.csv`, `outputs/feature_importance.csv`
- `data/processed/simulated_trip_features.csv`
- `reports/demo_daily_report.md`

Kaggle/UCI 공개 benchmark를 제외한 상태에서 유지 가능한 현재 실험은 다음이다.

- Mendeley smartphone sensor
- OBD-II/CAN Driving Behavior
- KIT Automotive OBD-II

추가 대안으로는 이미 다운로드/확인된 APS Failure at Scania Trucks와 MetroPT-3을 사용할 수 있지만, APS는 feature가 익명화되어 설명력이 낮고 MetroPT-3은 차량 데이터가 아니라 설비 시계열 이상 탐지에 더 가깝다.

## 최종 정리 문장

보고서에는 다음처럼 명확히 쓰는 것이 안전하다.

> 본 프로젝트는 실제 차량/센서 데이터셋인 Mendeley, OBD-II/CAN, KIT OBD-II를 중심으로 주행 습관 분류를 수행했고, Kaggle Vehicle Maintenance Telemetry와 UCI AI4I는 정비/예지정비 구조를 검증하기 위한 공개 benchmark 데이터셋으로 사용했다.
