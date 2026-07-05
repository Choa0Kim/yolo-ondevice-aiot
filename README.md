# yolo-ondevice-aiot

스마트팩토리/물류창고 환경의 AMR 안전 주행을 가정하고, 카메라 입력을 통해 작업자와 장애물 등 위험 객체를 실시간으로 감지하는 온디바이스 AIoT 비전 시스템 미니프로젝트입니다.

YOLO 모델을 소량 데이터로 파인튜닝한 뒤 ONNX로 변환하여 온디바이스 추론 가능성을 검증하고, 감지 결과를 MQTT로 전송하여 Node-RED 대시보드에서 시각화합니다.

## 목표

- 제조/물류 도메인 위험 객체 감지용 YOLO 모델 파인튜닝
- ONNX 변환을 통한 온디바이스 추론 준비
- MQTT 기반 감지 결과 publish
- Node-RED 기반 실시간 상태 시각화
- 사진 이미지 기반 모델 성능 검증
- 임의의 동영상 기반 실시간 시스템 검증

## 시스템 구조

```text
Camera / Video
  -> YOLO fine-tuned model
  -> ONNX Runtime inference
  -> Risk level calculation
  -> MQTT publish
  -> Node-RED dashboard
```

## 권장 개발 환경

| 작업 | 환경 |
|---|---|
| YOLO 파인튜닝 | Google Colab T4 |
| ONNX export | Google Colab T4 또는 로컬 |
| ONNX Runtime 추론 | 로컬 노트북 |
| MQTT / Node-RED | 로컬 노트북 |

## 프로젝트 구조

```text
.
├─ aiot_yolo_mini_project_plan.md
├─ requirements.txt
├─ data/
├─ models/
├─ notebooks/
├─ node-red/
└─ src/
```

## 진행 순서

1. GitHub 저장소 생성 및 초기 커밋
2. 감지 클래스 확정
3. 데이터 수집 및 라벨링
4. Colab T4에서 YOLO 파인튜닝
5. `best.pt`를 ONNX로 변환
6. 로컬에서 ONNX Runtime 추론 테스트
7. MQTT publish 구현
8. Node-RED dashboard 구성
9. 데모 영상과 결과 정리

## 감지 클래스 초안

- `person`
- `box`
- `traffic_cone`
- `forklift`

클래스 정의와 라벨링 기준은 [docs/dataset_guide.md](docs/dataset_guide.md)를 참고합니다.

## 검증 방식

| 검증 종류 | 입력 | 목적 |
|---|---|---|
| 모델 성능 검증 | 사진 이미지 | mAP, precision, recall, 클래스별 탐지 성능 확인 |
| 실시간 시스템 검증 | 임의의 동영상 | ONNX 추론, 위험도 판단, MQTT publish, Node-RED dashboard 확인 |

## 데이터셋 상태

최종 학습용 데이터셋은 로컬의 `data/processed/dataset_final`에 생성합니다. 원본 이미지와 라벨 파일은 GitHub에 올리지 않습니다.

현재 최종 데이터셋 분포:

| Split | Images | person | box | traffic_cone | forklift |
|---|---:|---:|---:|---:|---:|
| train | 813 | 410 | 857 | 1521 | 79 |
| val | 113 | 91 | 163 | 118 | 23 |

데이터 출처와 클래스 매핑은 [docs/dataset_guide.md](docs/dataset_guide.md)를 참고합니다.

## 학습 및 변환

Colab T4 기반 학습, validation 이미지 예측, ONNX 변환 절차는 [docs/training_colab_guide.md](docs/training_colab_guide.md)에 정리했습니다.

재현용 스크립트:

```text
scripts/train_yolov8.py
scripts/predict_validation.py
scripts/export_onnx.py
```

## ONNX 실시간 추론

로컬 노트북에서 `best.onnx`를 `models/best.onnx`에 배치한 뒤 ONNX Runtime으로 이미지/동영상 추론을 실행합니다. 모델 파일은 GitHub에 올리지 않습니다.

자세한 실행 절차는 [docs/realtime_system_guide.md](docs/realtime_system_guide.md)를 참고합니다.

```powershell
python src/run_onnx_detection.py `
  --model models/best.onnx `
  --source demo/input/warehouse_test.mp4 `
  --output output/detections
```

MQTT를 함께 사용할 경우:

```powershell
python src/run_onnx_detection.py `
  --model models/best.onnx `
  --source demo/input/warehouse_test.mp4 `
  --output output/detections `
  --mqtt-host localhost `
  --mqtt-topic aiot/detection
```

출력:

```text
output/detections/result_video.mp4
```

## 모델 성능

YOLOv8n 모델을 최종 데이터셋으로 파인튜닝한 결과는 다음과 같습니다.

| Metric | Value | 해석 |
|---|---:|---|
| Precision(B) | 0.87 | 예측한 객체 중 실제 정답 비율이 높아 오탐이 비교적 적음 |
| Recall(B) | 0.72 | 실제 객체 중 약 72%를 탐지하여 일부 미탐 존재 |
| mAP50(B) | 0.79 | IoU 0.5 기준 객체 탐지 성능은 양호 |
| mAP50-95(B) | 0.56 | 더 엄격한 bbox 위치 정확도 기준에서는 개선 여지 있음 |

`mAP50-95`가 상대적으로 낮은 이유는 여러 공개 데이터셋을 병합하면서 촬영 환경, 라벨링 기준, 클래스별 데이터 수가 균일하지 않기 때문으로 해석합니다. 특히 `forklift` 클래스의 데이터 수가 다른 클래스보다 적어 클래스별 성능 편차가 발생할 수 있습니다.

현재 결과는 미니프로젝트 프로토타입 기준으로는 충분하며, 이후 개선 방향은 다음과 같습니다.

- `forklift` 데이터 추가 확보
- 클래스별 데이터 수 균형 조정
- 제조/물류 배경 validation 이미지 추가
- bbox 라벨 품질 점검
- `YOLOv8s` 등 더 큰 모델과 비교 실험
- augmentation 설정 조정

## Git 관리 원칙

- 코드, 설정, 문서, Node-RED flow는 GitHub에 올립니다.
- 원본 데이터셋, 학습된 모델 파일, 데모 영상은 용량이 크므로 Git에 직접 올리지 않습니다.
- 개인 PDF, 참고 이미지, 임시 렌더링 파일은 Git에 올리지 않습니다.
- 모델과 데이터는 README에 다운로드 위치 또는 생성 방법을 기록합니다.
