# Figure 설명서

이 문서는 `outputs/figures` 폴더에 생성된 그래프가 각각 무엇을 의미하는지 정리한 설명서입니다.  
전체 프로젝트의 흐름은 `데이터 전처리 -> 머신러닝 학습 -> 테스트 데이터 예측 -> 성능 평가/시각화`입니다.

## 공통 해석 기준

| 그래프 종류 | 의미 | 확인할 점 |
| --- | --- | --- |
| `confusion_matrix` | 실제 라벨과 모델 예측 라벨의 교차표 | 대각선 값이 클수록 정답 예측이 많음 |
| `feature_importance` | 모델 판단에 크게 기여한 feature 순위 | 어떤 센서/변수가 라벨 구분에 중요한지 확인 |
| `f1_scores` | 클래스별 F1-score 비교 | 라벨 불균형이 있을 때 Accuracy만으로 놓치는 성능 차이를 확인 |
| `feature_distribution` / `sensor_distribution` | 주요 feature의 라벨별 분포 | 라벨별 데이터 패턴이 실제로 구분되는지 확인 |

> 참고: 이 프로젝트의 `feature_importance`는 트리 모델의 importance가 아니라, 클래스 간 분산 비율을 기반으로 계산한 해석용 중요도입니다. `vehicle_maintenance`의 importance도 이상 탐지 모델 자체가 아니라 비교 해석을 위해 별도 학습한 class-centroid 기준 중요도입니다.

## 1. Mendeley 스마트폰 센서 실험

- 실험 목적: 스마트폰 가속도/자이로 센서로 `normal` / `aggressive` 주행 습관을 분류
- 모델: standardized k-NN
- 성능: Accuracy `0.826`, Macro F1 `0.818`
- 주요 feature: `acc_magnitude`, `gyro_magnitude`, `acc_abs_x`, `gyro_abs_x`, `acc_abs_y`

| 파일 | 의미 | 해석 포인트 |
| --- | --- | --- |
| [mendeley_confusion_matrix.png](./mendeley_confusion_matrix.png) | Mendeley 테스트 데이터의 실제 주행 습관과 예측 결과 비교 | normal 1107건, aggressive 1835건을 맞췄고, normal/aggressive 사이 오분류도 일부 존재 |
| [mendeley_feature_importance.png](./mendeley_feature_importance.png) | 주행 습관 분류에 중요한 스마트폰 센서 feature 순위 | 가속도/자이로 magnitude가 상위라서 움직임의 전체 크기가 주행 습관 구분에 중요함 |
| [mendeley_f1_scores.png](./mendeley_f1_scores.png) | normal/aggressive 클래스별 F1-score 비교 | 두 클래스 모두 비교적 균형 있게 예측되는지 확인하는 그래프 |
| [mendeley_sensor_distribution.png](./mendeley_sensor_distribution.png) | 주요 센서값의 라벨별 분포 | normal과 aggressive 주행의 센서 패턴이 얼마나 겹치거나 분리되는지 확인 |

## 2. OBD-II/CAN 운전 습관 실험

- 실험 목적: 차량 내부 OBD-II/CAN 신호로 `moderate` / `aggressive` 주행 습관을 분류
- 모델: standardized class-centroid
- 성능: Accuracy `0.976`, Macro F1 `0.965`
- 주요 feature: `relative_throttle_position`, `accelerator_pedal_d`, `accelerator_pedal_e`, `throttle_position`, `intake_pressure`

| 파일 | 의미 | 해석 포인트 |
| --- | --- | --- |
| [obd_can_confusion_matrix.png](./obd_can_confusion_matrix.png) | OBD/CAN 테스트 데이터의 실제 라벨과 예측 라벨 비교 | moderate 107168건, aggressive 28294건을 맞춰 전체 실험 중 가장 안정적인 결과 |
| [obd_can_feature_importance.png](./obd_can_feature_importance.png) | OBD/CAN 주행 습관 분류에 중요한 차량 내부 신호 순위 | throttle, accelerator pedal, intake pressure 계열이 aggressive 주행 구분에 중요함 |
| [obd_can_f1_scores.png](./obd_can_f1_scores.png) | moderate/aggressive 클래스별 F1-score 비교 | 라벨별 성능이 모두 높아 차량 내부 신호가 주행 습관 분류에 효과적임 |
| [obd_can_feature_distribution.png](./obd_can_feature_distribution.png) | 주요 OBD/CAN feature의 라벨별 분포 | engine load, speed 등에서 moderate/aggressive 분포 차이를 확인 |

## 3. Vehicle Maintenance 이상 탐지 실험

- 실험 목적: 차량 정비 telemetry로 `normal` / `issue` 상태를 판정
- 모델: robust z-score anomaly detector
- 성능: Accuracy `0.978`, Macro F1 `0.791`, threshold `0.123`
- 주요 feature: `battery_voltage_v`, `brake_temp_c`, `brake_fluid_level_psi`, `battery_current_a`, `vibration_level`

| 파일 | 의미 | 해석 포인트 |
| --- | --- | --- |
| [vehicle_maintenance_confusion_matrix.png](./vehicle_maintenance_confusion_matrix.png) | 정비 데이터의 실제 normal/issue와 예측 결과 비교 | issue 8건을 모두 issue로 잡았고, normal 11건은 issue로 오탐지됨 |
| [vehicle_maintenance_feature_importance.png](./vehicle_maintenance_feature_importance.png) | 정비 상태 구분에 중요한 telemetry feature 순위 | 배터리 전압, 브레이크 온도, 브레이크 오일 압력 계열이 상태 구분에 중요함 |
| [vehicle_maintenance_f1_scores.png](./vehicle_maintenance_f1_scores.png) | normal/issue 클래스별 F1-score 비교 | issue 데이터가 적어 issue F1은 낮지만, recall 관점에서는 issue를 놓치지 않음 |
| [vehicle_maintenance_feature_distribution.png](./vehicle_maintenance_feature_distribution.png) | 정비 관련 feature의 normal/issue 분포 | battery voltage, brake temperature, coolant temperature에서 정상/이상 분포 차이를 확인 |

## 4. KIT Automotive OBD-II 실험

- 실험 목적: trip 단위 OBD-II 로그로 `normal` / `free_flow` / `traffic` 도로 조건을 분류
- 모델: standardized class-centroid
- 성능: Accuracy `0.526`, Macro F1 `0.420`
- 주요 feature: `coolant_temp_mean`, `pedal_e_max`, `pedal_d_max`, `rpm_mean`, `speed_mean`

| 파일 | 의미 | 해석 포인트 |
| --- | --- | --- |
| [automotive_obd_ii_confusion_matrix.png](./automotive_obd_ii_confusion_matrix.png) | KIT OBD-II trip 데이터의 실제 도로 조건과 예측 결과 비교 | 테스트 trip 수가 19개로 작아 클래스별 성능 변동이 큼 |
| [automotive_obd_ii_feature_importance.png](./automotive_obd_ii_feature_importance.png) | 도로 조건 분류에 중요한 trip-level feature 순위 | 냉각수 온도 평균, 페달 최대값, RPM/속도 평균이 주요 feature |
| [automotive_obd_ii_f1_scores.png](./automotive_obd_ii_f1_scores.png) | normal/free_flow/traffic 클래스별 F1-score 비교 | free_flow, traffic 라벨의 데이터 수가 적어 성능이 낮게 나타남 |
| [automotive_obd_ii_feature_distribution.png](./automotive_obd_ii_feature_distribution.png) | trip-level feature의 도로 조건별 분포 | speed_mean, rpm_mean 분포를 통해 도로 조건별 패턴 차이를 확인 |

## 5. AI4I 예지정비 벤치마크 실험

- 실험 목적: 예지정비 벤치마크 데이터로 `normal` / `failure` 상태를 분류
- 모델: standardized class-centroid
- 성능: Accuracy `0.726`, Macro F1 `0.496`
- 주요 feature: `torque_nm`, `tool_wear_min`, `air_temperature_k`, `rotational_speed_rpm`, `process_temperature_k`

| 파일 | 의미 | 해석 포인트 |
| --- | --- | --- |
| [ai4i_confusion_matrix.png](./ai4i_confusion_matrix.png) | AI4I 테스트 데이터의 실제 normal/failure와 예측 결과 비교 | failure 63건을 맞췄지만 normal 663건을 failure로 예측해 오탐이 많음 |
| [ai4i_feature_importance.png](./ai4i_feature_importance.png) | 고장 여부 분류에 중요한 feature 순위 | torque가 가장 큰 중요도를 가지며, tool wear와 temperature도 보조적으로 중요함 |
| [ai4i_f1_scores.png](./ai4i_f1_scores.png) | normal/failure 클래스별 F1-score 비교 | failure 라벨이 적어 클래스별 성능 불균형을 확인할 수 있음 |
| [ai4i_feature_distribution.png](./ai4i_feature_distribution.png) | 주요 예지정비 feature의 normal/failure 분포 | rotational speed, torque, tool wear에서 고장/정상 분포 차이를 확인 |

## 발표에서 활용하는 방법

1. `confusion_matrix`는 모델이 실제로 어떤 라벨을 맞추고 틀렸는지 보여줄 때 사용한다.
2. `feature_importance`는 머신러닝 알고리즘이 어떤 센서 feature를 근거로 판단했는지 설명할 때 사용한다.
3. `f1_scores`는 Accuracy만으로 부족한 클래스별 성능 비교를 보여줄 때 사용한다.
4. `feature_distribution`은 전처리와 feature engineering이 실제로 라벨 차이를 드러내는지 설명할 때 사용한다.

## 핵심 요약

- 가장 성능이 좋은 실험은 OBD-II/CAN 운전 습관 분류이며, Macro F1 `0.965`이다.
- Mendeley 스마트폰 센서 실험은 센서 기반 주행 습관 분류 기준선 역할을 한다.
- Vehicle Maintenance 실험은 정상 기준을 학습한 뒤 새 telemetry를 이상 후보로 판정하는 이상 탐지 구조를 보여준다.
- KIT Automotive OBD-II와 AI4I는 추가 검증 성격이 강하며, 데이터 수와 라벨 불균형 때문에 성능 개선 여지가 있다.
