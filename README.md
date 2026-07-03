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

## Git 관리 원칙

- 코드, 설정, 문서, Node-RED flow는 GitHub에 올립니다.
- 원본 데이터셋, 학습된 모델 파일, 데모 영상은 용량이 크므로 Git에 직접 올리지 않습니다.
- 개인 PDF, 참고 이미지, 임시 렌더링 파일은 Git에 올리지 않습니다.
- 모델과 데이터는 README에 다운로드 위치 또는 생성 방법을 기록합니다.
