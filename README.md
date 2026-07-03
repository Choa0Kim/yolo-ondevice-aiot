# On-device AIoT Driving Vision Mini Project

YOLO 파인튜닝 모델을 ONNX로 변환하고, ONNX Runtime 추론 결과를 MQTT로 전송하여 Node-RED 대시보드에서 시각화하는 미니프로젝트입니다.

## 목표

- 무인주행 위험 객체 감지용 YOLO 모델 파인튜닝
- ONNX 변환을 통한 온디바이스 추론 준비
- MQTT 기반 감지 결과 publish
- Node-RED 기반 실시간 상태 시각화

## 시스템 구조

```text
Camera / Video
  -> YOLO fine-tuned model
  -> ONNX Runtime inference
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
- `car`
- `traffic_cone`
- `obstacle`

## Git 관리 원칙

- 코드, 설정, 문서, Node-RED flow는 GitHub에 올린다.
- 원본 데이터셋, 학습된 모델 파일, 데모 영상은 용량이 크므로 Git에 직접 올리지 않는다.
- 모델과 데이터는 README에 다운로드 위치 또는 생성 방법을 기록한다.

