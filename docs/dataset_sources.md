# 데이터셋 출처

확인일: 2026-06-01

| 우선순위 | 데이터셋 | 프로젝트 내 사용 목적 | URL | 접근 및 사용 참고 |
| --- | --- | --- | --- | --- |
| 1 | Phone sensor data while driving a car and normal or aggressive driving behaviour classification | 운전 습관 분류: normal / aggressive | https://data.mendeley.com/datasets/5stn873wft/1 | Mendeley Data 공개 데이터셋. 스마트폰을 차량 대시보드에 부착해 수집한 GPS, 속도, 가속도, 자이로 데이터를 포함한다. 라이선스는 CC BY 4.0이다. |
| 2 | OBD-II & CAN-Based Driving Behavior Dataset | OBD-II/CAN 기반 운전 스타일 분류: moderate / aggressive | https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset | Kaggle 계정과 API 토큰이 있어야 스크립트 다운로드가 가능하다. |
| 3 | NGSIM Vehicle Trajectories and Supporting Data | 차량 궤적 기반 급가속, 급제동, 정체 주행 feature 추출 | https://data.transportation.gov/Automobiles/Next-Generation-Simulation-NGSIM-Vehicle-Trajector/8ect-6jqj | 미국 DOT 공식 공개 데이터. 운전 습관 라벨은 없으므로 지도학습보다는 feature engineering, 이벤트 감지, 군집화 보조 데이터로 사용한다. |
| 4 | APS Failure at Scania Trucks | 차량 고장 및 예지정비 분류 | https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks | UCI 데이터셋 ID 421. 직접 ZIP 링크: https://archive.ics.uci.edu/static/public/421/aps%2Bfailure%2Bat%2Bscania%2Btrucks.zip |
| 5 | Vehicle Maintenance Telemetry Data | 차량 텔레메트리 기반 점검 추천 데모 | https://www.kaggle.com/datasets/tejalaveti2306/vehicle-maintenance-telemetry-data | 합성 차량 fleet 텔레메트리 데이터. Kaggle 계정과 API 토큰이 필요하다. |
| 6 | AI4I 2020 Predictive Maintenance Dataset | 예지정비 보조 벤치마크 | https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset | UCI 데이터셋 ID 601. 직접 ZIP 링크: https://cdn.uci-ics-mlr-prod.aws.uci.edu/601/ai4i%2B2020%2Bpredictive%2Bmaintenance%2Bdataset.zip |
| 7 | MetroPT-3 Dataset | 시계열 이상 탐지 보조 벤치마크 | https://archive.ics.uci.edu/dataset/791/metropt+3+dataset | UCI 데이터셋 ID 791. 직접 ZIP 링크: https://archive.ics.uci.edu/static/public/791/metropt%2B3%2Bdataset.zip |
| 보류 | UAH-DriveSet | 기존 1순위 후보였던 normal / drowsy / aggressive 운전 습관 데이터 | https://www.robesafe.uah.es/personal/eduardo.romera/uah-driveset/ | 현재 접근 불가 또는 다운로드 불안정으로 1차 구현 대상에서 제외한다. 나중에 접근이 복구되면 보조 비교 데이터로 다시 검토한다. |

## 추천 데이터 조합

- 운전 습관 분석 메인 데이터: Mendeley 스마트폰 센서 데이터 + OBD-II & CAN-Based Driving Behavior Dataset
- 운전 이벤트 및 feature engineering 보조 데이터: NGSIM Vehicle Trajectories and Supporting Data
- 차량 상태 및 이상 탐지 메인 데이터: APS Failure at Scania Trucks + Vehicle Maintenance Telemetry Data
- 보조 실험 데이터: 소규모 예지정비 벤치마크는 AI4I 2020, 대용량 시계열 이상 탐지는 MetroPT-3

## UAH-DriveSet 제외 사유

UAH-DriveSet은 계획서의 원래 1순위 후보였지만 현재 접근이 불가능하거나 다운로드 절차가 안정적이지 않다. 프로젝트 일정상 데이터 확보가 막히면 구현이 지연되므로, 1차 구현에서는 접근 가능한 Mendeley 스마트폰 센서 데이터와 OBD-II/CAN 데이터를 우선 사용한다.

UAH-DriveSet을 제외하면 `drowsy` 라벨은 바로 사용하기 어렵다. 대신 1차 모델의 운전 습관 분류는 `normal / aggressive` 또는 `moderate / aggressive` 이진 분류로 시작하고, 이후 데이터가 추가되면 `normal / aggressive / risky` 다중 분류로 확장한다.

## Mendeley 수동 다운로드

Mendeley Data 페이지에서 `Download All`을 눌러 CSV 파일을 내려받은 뒤 다음 위치에 둔다.

```text
data/raw/mendeley_phone_sensor/
```

## Kaggle 다운로드 명령어

```bash
kaggle datasets download -d isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset -p data/raw/obd_can --unzip
kaggle datasets download -d tejalaveti2306/vehicle-maintenance-telemetry-data -p data/raw/vehicle_maintenance --unzip
```

## NGSIM 다운로드 참고

NGSIM은 미국 DOT 데이터 포털에서 직접 내려받는다. 라벨이 있는 운전 습관 분류 데이터는 아니므로, `speed`, `acceleration`, `jerk`, `hard_brake_count`, `idle_time` 같은 feature를 추출하는 보조 데이터로 사용한다.

## UCI 다운로드 명령어

```bash
mkdir -p data/raw/aps data/raw/ai4i data/raw/metropt3
curl -L "https://archive.ics.uci.edu/static/public/421/aps%2Bfailure%2Bat%2Bscania%2Btrucks.zip" -o data/raw/aps/aps_failure.zip
curl -L "https://cdn.uci-ics-mlr-prod.aws.uci.edu/601/ai4i%2B2020%2Bpredictive%2Bmaintenance%2Bdataset.zip" -o data/raw/ai4i/ai4i2020.zip
curl -L "https://archive.ics.uci.edu/static/public/791/metropt%2B3%2Bdataset.zip" -o data/raw/metropt3/metropt3.zip
```
