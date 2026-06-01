# 프로젝트 구현 계획

## 목표

차량 주행 데이터와 차량 상태 데이터를 분석해 운전 습관을 분류하고, 차량 부품 부담과 이상 가능성을 추정해 일일 차량 점검 리포트를 생성한다.

## 핵심 기능

| 단계 | 구현 내용 |
| --- | --- |
| 데이터 준비 | 공개 데이터셋 또는 합성 feature 데이터 로드 |
| 전처리 | 결측치 처리, 단위 통일, 숫자 feature 정리 |
| Feature 추출 | 속도, 가속도, jerk, yaw rate, RPM, 엔진 부하, 냉각수 온도, 배터리 전압, 이벤트 횟수 |
| 운전 습관 분류 | normal / aggressive / risky 분류 |
| 이상 탐지 | 차량 상태 feature 기반 이상 점수 계산 |
| 점검 권장 | 이벤트와 차량 상태를 규칙 기반으로 부품 점검 항목에 매핑 |
| 리포트 생성 | 사람이 읽기 쉬운 한국어 일일 차량 점검 리포트 생성 |
| 평가 | Accuracy, Precision, Recall, F1-score, Confusion Matrix 저장 |

## 1차 구현 전략

현재 로컬 Python 환경에는 `scikit-learn`이 없어 Random Forest와 Isolation Forest를 바로 실행할 수 없다. 따라서 1차 구현은 다음 baseline으로 구성한다.

- 운전 습관 분류: 표준화된 feature centroid 기반 분류기
- 차량 상태 이상 탐지: robust z-score 기반 이상 점수
- 점검 추천: PDF 계획서의 이벤트-부품 부담 매핑을 rule-based 로직으로 구현

이 구조는 실제 데이터셋을 확보한 뒤 다음 모델로 교체할 수 있다.

- `sklearn.ensemble.RandomForestClassifier`
- `sklearn.ensemble.IsolationForest`
- `sklearn.cluster.KMeans`

## 산출물

- 학습/평가 결과 JSON
- Confusion Matrix CSV
- Feature importance CSV
- 일일 차량 점검 리포트 Markdown
