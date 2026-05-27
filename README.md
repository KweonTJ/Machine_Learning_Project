# Machine_Learning_Project

# ROS2 + Python 기반 Astra 3D Depth Camera 스쿨존 돌발 보행자 감지 ADAS 시뮬레이터

## 1. 프로젝트 개요

본 프로젝트는 어린이 보호구역에서 장애물 뒤에서 보행자가 갑자기 튀어나오는 상황을 감지하기 위한 ADAS 소프트웨어 시뮬레이터이다.

Orbbec Astra 3D Depth Camera 1대를 차량 전방 센서로 가정하고, RGB 영상에서는 YOLO로 보행자를 탐지하며, Depth Map과 Point Cloud를 이용해 보행자의 3D 위치를 계산한다.

이후 차량 진행 경로인 `3D Danger Corridor` 침범 여부와 TTC(Time To Collision)를 기반으로 위험도를 판단하고, 결과를 Python Dashboard에 시각화한다.

위험 상태는 다음 4개로 분류한다.

```text
SAFE
CAUTION
WARNING
BRAKE
```

---

## 2. 주요 기능

- Astra 3D Depth Camera 입력
- ROS2 Topic 기반 데이터 처리
- YOLO 기반 보행자 탐지
- Depth Map 기반 거리 측정
- Point Cloud 기반 3D 위치 추정
- 3D Danger Corridor 침범 판단
- TTC 기반 충돌 위험도 계산
- Random Forest 기반 위험도 분류
- Python ADAS Dashboard 시각화

---

## 3. 시스템 구조

```text
Orbbec Astra 3D Depth Camera
   ↓
ROS2 Camera Node
   ↓
RGB / Depth / PointCloud Topic
   ↓
YOLO Pedestrian Detection Node
   ↓
Point Cloud Feature Extraction Node
   ↓
Risk Classification Node
   ↓
Python ADAS Dashboard Node
```

---

## 4. 사용 하드웨어

| 하드웨어 | 용도 |
|---|---|
| Orbbec Astra 3D Depth Camera | RGB 영상, Depth Map, Point Cloud 입력 |
| 노트북 / PC | ROS2, Python, YOLO, Open3D, ML 모델 실행 |
| USB 케이블 | Astra 카메라 연결 |
| 삼각대 / 거치대 | 카메라 고정 |
| 박스 / 의자 / 파티션 | 가림 장애물 역할 |
| 줄자 | 거리 오차 측정 |
| 바닥 테이프 | 차량 진행 경로 표시 |
| 보행자 타깃 | 사람, 인형, 출력 이미지 등 |

사용하지 않는 하드웨어:

```text
Arduino
LED
Buzzer
Servo Motor
LiDAR
Radar
초음파 센서
RC카
로봇팔
TOPST
```

---

## 5. 사용 소프트웨어

| 소프트웨어 | 용도 |
|---|---|
| Ubuntu 22.04 | ROS2 Humble 환경 |
| ROS2 Humble | Topic 기반 시스템 구성 |
| Python 3.10 | ROS2 Python Node 개발 |
| rclpy | Python ROS2 Node 작성 |
| OpenCV | 영상 처리 및 화면 출력 |
| NumPy | Depth / Point Cloud 배열 처리 |
| Pandas | CSV 저장 및 분석 |
| Ultralytics YOLO | 보행자 탐지 |
| PyTorch | YOLO 실행 |
| Open3D | Point Cloud 처리 |
| scikit-learn | Random Forest 학습 |
| Matplotlib | 결과 시각화 |
| Joblib | 모델 저장 |
| OpenNI2 / Astra SDK / Orbbec ROS2 Driver | Astra 카메라 연동 |

---

## 6. 설치 방법

### 6.1 ROS2 환경

Ubuntu 22.04 + ROS2 Humble 환경을 권장한다.

```bash
source /opt/ros/humble/setup.bash
```

---

### 6.2 Python 가상환경

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 6.3 Python 패키지 설치

```bash
pip install opencv-python numpy pandas matplotlib scikit-learn joblib
pip install ultralytics torch torchvision
pip install open3d
```

---

### 6.4 Astra 카메라 연동

Astra 카메라는 환경에 따라 다음 중 하나를 사용한다.

```text
1. Orbbec ROS2 Driver
2. ros2_astra_camera
3. OpenNI2 + Python Bridge Node
```

먼저 다음을 확인한다.

```bash
ros2 topic list
```

정상 연결 시 RGB, Depth, PointCloud 관련 topic이 출력되어야 한다.

예상 Topic:

```text
/camera/color/image_raw
/camera/depth/image_raw
/camera/depth/points
/camera/color/camera_info
```

---

## 7. 폴더 구조

```text
schoolzone_adas_ws/
 └─ src/
    └─ schoolzone_adas/
       ├─ package.xml
       ├─ setup.py
       ├─ launch/
       │  └─ schoolzone_adas.launch.py
       ├─ config/
       │  └─ params.yaml
       ├─ models/
       │  ├─ yolo_model.pt
       │  └─ risk_classifier.pkl
       ├─ data/
       │  ├─ rgb/
       │  ├─ depth/
       │  ├─ pointcloud/
       │  └─ features.csv
       └─ schoolzone_adas/
          ├─ __init__.py
          ├─ pedestrian_detector_node.py
          ├─ pointcloud_feature_node.py
          ├─ risk_classifier_node.py
          ├─ adas_dashboard_node.py
          └─ data_logger_node.py
```

---

## 8. ROS2 노드 구성

| Node | 역할 |
|---|---|
| `astra_camera_node` | Astra RGB / Depth / PointCloud 입력 |
| `pedestrian_detector_node` | YOLO 기반 보행자 탐지 |
| `pointcloud_feature_node` | 3D 위치, TTC, 위험영역 침범률 계산 |
| `risk_classifier_node` | SAFE / CAUTION / WARNING / BRAKE 분류 |
| `adas_dashboard_node` | RGB, Depth, Top View, 위험 상태 시각화 |
| `data_logger_node` | 실험 데이터 저장 |

---

## 9. ROS2 Topic 설계

| Topic | Type | 설명 |
|---|---|---|
| `/camera/color/image_raw` | `sensor_msgs/msg/Image` | RGB 영상 |
| `/camera/depth/image_raw` | `sensor_msgs/msg/Image` | Depth 영상 |
| `/camera/depth/points` | `sensor_msgs/msg/PointCloud2` | Point Cloud |
| `/camera/color/camera_info` | `sensor_msgs/msg/CameraInfo` | 카메라 내부 파라미터 |
| `/adas/person_bbox` | `std_msgs/msg/String` | 보행자 Bounding Box |
| `/adas/features` | `std_msgs/msg/String` | 3D Feature |
| `/adas/risk_state` | `std_msgs/msg/String` | 위험 상태 |
| `/adas/dashboard_image` | `sensor_msgs/msg/Image` | Dashboard 이미지 |

---

## 10. 알고리즘 흐름

```text
1. Astra 카메라에서 RGB / Depth / PointCloud Topic 발행
2. RGB 영상에서 YOLO로 보행자 탐지
3. 보행자 Bounding Box 추출
4. Depth / PointCloud에서 보행자 영역의 3D 점군 추출
5. 보행자 3D 중심점 계산
6. 3D Danger Corridor 침범 여부 판단
7. 거리, 좌우 위치, TTC, 이동속도 Feature 생성
8. Random Forest로 위험도 분류
9. Python Dashboard에 결과 표시
```

---

## 11. 3D Danger Corridor

차량이 정면으로 진행한다고 가정하고 전방 위험영역을 정의한다.

```text
x축: 좌우 방향
y축: 상하 방향
z축: 전방 거리
```

예시:

```text
-0.6 m < x < +0.6 m
0.6 m < z < 4.0 m
```

보행자가 이 영역에 들어오고 TTC가 짧으면 `BRAKE` 상태로 판단한다.

---

## 12. 위험 상태 정의

| 상태 | 의미 |
|---|---|
| SAFE | 보행자 없음 또는 차량 경로 밖 |
| CAUTION | 보행자가 감지되었지만 직접 위험은 낮음 |
| WARNING | 보행자가 차량 경로 근처로 접근 |
| BRAKE | 보행자가 위험영역에 진입하여 제동 필요 |

---

## 13. Feature 목록

| Feature | 설명 |
|---|---|
| `person_detected` | 보행자 탐지 여부 |
| `centroid_x` | 보행자의 좌우 위치 |
| `centroid_z` | 보행자까지의 전방 거리 |
| `extent_x` | 보행자 점군의 폭 |
| `extent_y` | 보행자 점군의 높이 |
| `corridor_overlap_ratio` | 차량 진행 경로 침범률 |
| `lateral_velocity_x` | 보행자의 좌우 이동속도 |
| `approach_velocity_z` | 차량 기준 접근 속도 |
| `ttc` | 충돌 예상 시간 |
| `occlusion_flag` | 장애물 뒤 출현 여부 |
| `label` | 위험 상태 라벨 |

---

## 14. 머신러닝 모델

기본 모델은 `Random Forest Classifier`를 사용한다.

입력:

```text
person_detected
centroid_x
centroid_z
extent_x
extent_y
corridor_overlap_ratio
lateral_velocity_x
approach_velocity_z
ttc
occlusion_flag
```

출력:

```text
SAFE
CAUTION
WARNING
BRAKE
```

---

## 15. 실행 방법

워크스페이스 빌드:

```bash
cd schoolzone_adas_ws
colcon build
source install/setup.bash
```

카메라 노드 실행:

```bash
ros2 launch <astra_camera_package> <astra_launch_file>.launch.py
```

전체 시스템 실행:

```bash
ros2 launch schoolzone_adas schoolzone_adas.launch.py
```

개별 노드 실행 예시:

```bash
ros2 run schoolzone_adas pedestrian_detector_node
ros2 run schoolzone_adas pointcloud_feature_node
ros2 run schoolzone_adas risk_classifier_node
ros2 run schoolzone_adas adas_dashboard_node
```

---

## 16. 실험 시나리오

| 시나리오 | 상황 | 기대 상태 |
|---|---|---|
| S1 | 보행자 없음 | SAFE |
| S2 | 보행자가 멀리 있고 경로 밖 | SAFE / CAUTION |
| S3 | 보행자가 장애물 옆에서 등장 | CAUTION |
| S4 | 보행자가 차량 경로로 접근 | WARNING |
| S5 | 보행자가 Danger Corridor 진입 | BRAKE |
| S6 | 좌측 장애물 뒤에서 갑자기 출현 | WARNING / BRAKE |
| S7 | 우측 장애물 뒤에서 갑자기 출현 | WARNING / BRAKE |
| S8 | 보행자가 빠르게 횡단 | BRAKE |

---

## 17. 평가 지표

| 지표 | 설명 |
|---|---|
| Pedestrian Detection Rate | 보행자 탐지 성공률 |
| Depth Distance Error | 실제 거리와 측정 거리 차이 |
| 3D Corridor Accuracy | 위험영역 침범 판단 정확도 |
| Risk Classification Accuracy | 위험도 분류 정확도 |
| BRAKE Recall | 실제 제동 상황을 놓치지 않은 비율 |
| False Brake Rate | 불필요한 제동 발생 비율 |
| FPS | 실시간 처리 속도 |

자동차 안전 관점에서는 전체 정확도보다 `BRAKE Recall`을 더 중요하게 본다.

---

## 18. Dashboard 출력

Python Dashboard에는 다음 정보를 표시한다.

```text
RGB 보행자 탐지 화면
Depth Map
Point Cloud Top View
Danger Corridor
보행자 3D 위치
TTC
Risk State
FPS
```

---

## 19. 한계 및 개선 방향

| 한계 | 개선 방향 |
|---|---|
| 완전히 가려진 보행자는 감지 불가 | V2X, 도로 인프라 센서 추가 |
| 실외 강한 빛에서 Depth 오차 가능 | LiDAR / Radar 융합 |
| 실제 어린이와 성인 구분 어려움 | 어린이 데이터셋 추가 |
| 실내 실험 중심 | 실외 데이터 확장 |
| 데이터 수 부족 | 시나리오 반복 촬영 및 데이터 증강 |

---

## 20. 최종 목표

본 프로젝트는 Astra 3D Depth Camera 1대와 ROS2, Python을 이용하여 어린이 보호구역 돌발 보행자 상황을 3D 공간에서 감지하고, 머신러닝 기반 위험도 분류 결과를 Python Dashboard로 시각화하는 것을 목표로 한다.

핵심 구성:

```text
Astra 3D Depth Camera
+ ROS2
+ Python
+ YOLO Pedestrian Detection
+ Point Cloud
+ 3D Danger Corridor
+ TTC
+ Random Forest
+ ADAS Dashboard
```