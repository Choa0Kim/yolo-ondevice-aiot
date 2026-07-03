# YOLO 파인튜닝 기반 온디바이스 AIoT 무인주행 위험 객체 감지 미니프로젝트 계획

## 1. 프로젝트 개요

### 주제

**YOLO 파인튜닝 기반 온디바이스 AIoT 무인주행 위험 객체 감지 시스템**

### 목표

무인 주행 시스템에서 카메라 입력을 통해 위험 객체를 실시간으로 감지하고, 감지 결과를 MQTT로 전송하여 Node-RED 대시보드에서 시각화한다.  
YOLO 모델을 소량 데이터로 파인튜닝한 뒤 ONNX로 변환하여 온디바이스 추론 가능성을 검증한다.

### 전체 흐름

```text
카메라/동영상 입력
  -> YOLO 파인튜닝 모델 추론
  -> ONNX 변환 및 ONNX Runtime 추론
  -> 감지 결과 MQTT publish
  -> Node-RED MQTT subscribe
  -> 위험도 대시보드 시각화
```

## 2. 프로젝트 선정 이유

공통 프로젝트 소개자료의 Track3는 **온디바이스 AIoT 활용 무인 주행 시스템 구축**을 목표로 한다. 해당 주제에서는 임베디드 보드, 센서 데이터, 인공지능 모델, 온디바이스 추론, IoT 통신을 함께 이해하는 역량이 중요하다.

이 미니프로젝트는 단순히 YOLO 모델을 실행하는 수준이 아니라, 다음 역량을 함께 보여줄 수 있다.

- 무인주행 상황에 필요한 위험 객체 클래스 정의
- YOLO 기반 객체탐지 모델 파인튜닝
- ONNX 변환을 통한 경량 추론 준비
- MQTT 기반 AIoT 메시징
- Node-RED 기반 실시간 대시보드 구성
- 온디바이스 AI 모델 담당자로서의 역할 적합성 증명

## 3. 사용 기술

| 영역 | 기술 |
|---|---|
| 객체탐지 모델 | YOLOv8n 또는 YOLO 계열 nano 모델 |
| 모델 학습 | Python, PyTorch, Ultralytics |
| 추론 | OpenCV, ONNX Runtime |
| 모델 변환 | ONNX |
| IoT 메시징 | MQTT, Mosquitto |
| 시각화 | Node-RED Dashboard |
| 선택 확장 | Raspberry Pi, Jetson, Docker |

## 3-1. 개발 환경 전략

### 현재 로컬 환경

확인된 개발 환경:

| 항목 | 사양 |
|---|---|
| CPU | Intel Core Ultra 7 255H |
| Memory | 약 32GB |
| GPU | Intel Arc 내장 GPU |
| NPU | Intel AI Boost |
| OS | Windows |

### 진행 가능 여부

현재 노트북으로 프로젝트 전체를 진행할 수 있다. 다만 작업별 적합도가 다르다.

| 작업 | 로컬 노트북 가능 여부 | 권장 환경 |
|---|---|---|
| 데이터 정리/라벨링 | 가능 | 로컬 |
| YOLO 사전학습 모델 추론 | 가능 | 로컬 |
| YOLO 파인튜닝 | 가능하지만 느릴 수 있음 | Colab T4 권장 |
| ONNX export | 가능 | Colab 또는 로컬 |
| ONNX Runtime CPU 추론 | 가능 | 로컬 |
| MQTT publish | 가능 | 로컬 |
| Node-RED dashboard | 가능 | 로컬 |
| 웹캠 실시간 데모 | 가능 | 로컬 |

### 권장 진행 방식

가장 안정적인 방식은 **학습은 Colab T4에서 수행하고, AIoT 연동은 로컬에서 수행하는 것**이다.

```text
Colab T4
  -> YOLO 파인튜닝
  -> best.pt 생성
  -> ONNX export
  -> best.onnx 다운로드

Local Windows Laptop
  -> ONNX Runtime 추론
  -> MQTT publish
  -> Node-RED dashboard
  -> 웹캠/동영상 데모
```

### 이유

- Intel Arc GPU는 일반적인 PyTorch CUDA 학습 환경으로 바로 사용하기 어렵다.
- CPU만으로 YOLO 파인튜닝은 가능하지만 학습 시간이 길어질 수 있다.
- Colab T4는 CUDA 기반 학습이 가능하므로 YOLOv8n 파인튜닝에 적합하다.
- 로컬 노트북은 CPU, 메모리, 저장장치가 충분하므로 ONNX 추론, MQTT, Node-RED, 데모 실행에는 충분하다.
- Intel NPU는 흥미로운 요소지만, 하루 반 미니프로젝트에서는 OpenVINO/NPU 최적화까지 포함하면 범위가 커진다. 따라서 선택 확장으로 둔다.

### 최종 권장 환경 분리

| 구분 | 담당 작업 |
|---|---|
| Colab T4 | 학습, 평가, ONNX 변환 |
| 로컬 노트북 | 추론 코드, MQTT, Node-RED, 발표 데모 |

## 4. 감지 클래스

하루 반 일정에서는 클래스 수를 너무 많이 늘리지 않는 것이 중요하다. 권장 클래스는 4개다.

| 클래스 | 선정 이유 |
|---|---|
| `person` | 무인주행 안전 판단에서 가장 중요한 객체 |
| `car` 또는 `vehicle` | 주행 환경의 핵심 객체 |
| `traffic_cone` | 공사 구역, 장애물, 회피 상황 표현 가능 |
| `obstacle` | 박스, 가방, 임의 장애물 등 정지/감속 판단에 활용 |

선택적으로 `stop_sign`을 추가할 수 있으나, 한국 환경에서 직접 수집하기 어려울 수 있으므로 우선순위는 낮게 둔다.

## 5. 데이터 계획

### 데이터 규모

| 기준 | 수량 |
|---|---:|
| 최소 | 클래스당 30-50장 |
| 권장 | 클래스당 50-80장 |
| 전체 | 약 150-300장 |

### 데이터 수집 방식

- 직접 촬영한 실내/실외 이미지
- 공개 데이터셋 일부 활용
- 동영상에서 프레임 추출
- 주행 상황과 유사한 시점의 이미지 우선 수집

### 라벨링 방식

- Roboflow, CVAT, LabelImg 중 하나 사용
- YOLO format으로 export
- train/valid split 구성

예상 구조:

```text
dataset/
  images/
    train/
    val/
  labels/
    train/
    val/
  data.yaml
```

## 6. 구현 범위

### 필수 구현

- YOLOv8n 기반 커스텀 데이터 파인튜닝
- 학습 결과 모델 저장
- 이미지 또는 동영상 객체탐지 결과 저장
- ONNX export
- ONNX Runtime 추론 코드 작성
- MQTT publish
- Node-RED dashboard에서 감지 결과 시각화

### 선택 구현

- 웹캠 실시간 추론
- 위험도 판단 로직
- Raspberry Pi 또는 Jetson 보드 추론
- Docker 기반 실행 환경 구성
- FPS, 모델 크기, 추론 시간 비교

## 7. 위험도 판단 로직

정교한 주행 제어가 아니라, 미니프로젝트에서는 객체탐지 결과를 기반으로 단순한 상태 판단을 구현한다.

```python
if "person" in detected_classes and person_bbox_bottom > frame_height * 0.55:
    risk = "STOP"
elif "obstacle" in detected_classes or "traffic_cone" in detected_classes:
    risk = "SLOW"
else:
    risk = "GO"
```

위험도 상태:

| 상태 | 의미 |
|---|---|
| `GO` | 주행 가능 |
| `SLOW` | 장애물 또는 주의 객체 감지 |
| `STOP` | 사람 또는 즉시 정지 대상 감지 |

## 7-1. 검증 전략

이 프로젝트의 검증은 두 가지로 나누어 진행한다.

1. **모델 성능 검증**
2. **실시간 시스템 검증**

두 검증의 목적이 다르므로 입력 데이터와 확인 항목도 다르게 설정한다.

### 1. 모델 성능 검증: 사진 이미지 기반

모델이 제조/물류 도메인 객체를 잘 탐지하는지는 사진 이미지로 검증한다.

사용 데이터:

- 학습에 사용하지 않은 validation/test 이미지
- 제조/물류 환경과 유사한 이미지
- 작업자, 박스, 팔레트, 지게차, 안전콘 등이 포함된 이미지

확인 항목:

| 항목 | 설명 |
|---|---|
| mAP50 | 객체탐지 모델의 기본 성능 지표 |
| precision | 탐지한 객체 중 실제 정답 비율 |
| recall | 실제 객체 중 모델이 찾아낸 비율 |
| 클래스별 성능 | `person`, `box`, `traffic_cone`, `forklift/vehicle`별 성능 |
| 오탐 사례 | 객체가 아닌 것을 잘못 탐지한 경우 |
| 미탐 사례 | 실제 객체를 탐지하지 못한 경우 |

산출물:

```text
runs/detect/val/
demo/result_images/
```

README에는 다음 내용을 포함한다.

```text
test image N장 기준
- person mAP50:
- box mAP50:
- traffic_cone mAP50:
- forklift/vehicle mAP50:
```

### 2. 실시간 시스템 검증: 임의의 동영상 기반

실시간 시스템 검증은 노트북 카메라 대신 임의의 동영상 파일을 사용한다.  
동영상의 각 프레임을 카메라 입력처럼 읽어 ONNX 추론, 위험도 판단, MQTT 전송, Node-RED 시각화를 검증한다.

입력 예시:

```text
demo/input/warehouse_test.mp4
```

처리 흐름:

```text
warehouse_test.mp4
  -> frame 단위 읽기
  -> ONNX Runtime 추론
  -> 객체 bbox/class/confidence 생성
  -> 위험도 GO/SLOW/STOP 계산
  -> MQTT publish
  -> Node-RED dashboard 실시간 갱신
  -> 결과 영상 저장
```

확인 항목:

| 항목 | 확인 방법 |
|---|---|
| ONNX 추론 | `.onnx` 모델로 동영상 프레임을 처리하는지 |
| 객체탐지 표시 | 영상에 bbox, class, confidence가 표시되는지 |
| 위험도 판단 | 객체 위치와 종류에 따라 `GO`, `SLOW`, `STOP`이 바뀌는지 |
| FPS 측정 | 프레임 처리 속도가 출력되는지 |
| MQTT 연동 | `aiot/detection` topic으로 메시지가 publish되는지 |
| Node-RED 연동 | 대시보드 값이 실시간으로 갱신되는지 |
| 결과 저장 | bbox와 위험도가 표시된 결과 영상이 저장되는지 |

산출물:

```text
demo/output/result_video.mp4
node-red/flow.json
```

GitHub에는 원본/결과 동영상 파일을 직접 올리지 않는다.  
대신 README에는 짧은 GIF, 캡처 이미지, 실행 방법, 결과 설명을 기록한다.

### 검증 방식 요약

| 검증 종류 | 입력 | 목적 | 주요 산출물 |
|---|---|---|---|
| 모델 성능 검증 | 사진 이미지 | 탐지 정확도 확인 | mAP, precision, recall, 결과 이미지 |
| 실시간 시스템 검증 | 임의의 동영상 | ONNX/MQTT/Node-RED 파이프라인 확인 | 결과 영상, MQTT 로그, 대시보드 캡처 |

## 8. MQTT 메시지 설계

### Topic

```text
aiot/detection
```

### Payload 예시

```json
{
  "timestamp": "2026-07-04T15:20:10",
  "device_id": "edge-camera-01",
  "objects": [
    {
      "class": "person",
      "confidence": 0.87,
      "bbox": [120, 80, 260, 420]
    }
  ],
  "risk_level": "STOP",
  "fps": 12.4
}
```

## 9. Node-RED 대시보드 구성

Node-RED에서는 MQTT 메시지를 구독하여 실시간 상태를 확인한다.

구성 요소:

- 현재 위험도: `GO`, `SLOW`, `STOP`
- 감지 객체 목록
- 객체별 confidence
- 현재 FPS
- 최근 MQTT 메시지 로그
- 위험도별 색상 표시
  - `GO`: green
  - `SLOW`: yellow
  - `STOP`: red

## 10. 1.5일 작업 일정

### Day 1

| 시간 | 작업 | 산출물 |
|---|---|---|
| 09:00-10:00 | 문제 정의, 클래스 선정, 개발 환경 구성 | 클래스 목록, 환경 준비 |
| 10:00-12:00 | 데이터 수집 | 이미지 150-300장 |
| 12:00-14:00 | 라벨링 및 YOLO format 정리 | `dataset/`, `data.yaml` |
| 14:00-16:00 | YOLOv8n 파인튜닝 | `best.pt`, 학습 로그 |
| 16:00-17:00 | 평가 및 샘플 추론 | mAP, precision, recall, 결과 이미지 |
| 17:00-18:00 | 문제 보완 | 데이터/라벨 수정 또는 재학습 |

### Day 2 반나절

| 시간 | 작업 | 산출물 |
|---|---|---|
| 09:00-10:00 | ONNX export | `best.onnx` |
| 10:00-11:00 | ONNX Runtime 추론 코드 작성 | `onnx_inference.py` |
| 11:00-12:00 | MQTT publish 연동 | `onnx_inference_mqtt.py` |
| 12:00-13:00 | Node-RED dashboard 구성 | `flow.json`, 대시보드 |
| 13:00-14:00 | README, 구조도, 데모 영상 정리 | 발표용 산출물 |

## 11. 우선순위

### 1순위

- YOLO 파인튜닝
- 결과 이미지 저장
- 성능 지표 정리

### 2순위

- ONNX export
- ONNX Runtime 추론

### 3순위

- MQTT publish
- Node-RED dashboard

### 4순위

- 위험도 판단 로직
- 웹캠 실시간 추론
- 실제 보드 테스트

## 12. 최종 산출물

```text
runs/detect/train/weights/best.pt
models/best.onnx
src/train_yolo.py
src/onnx_inference.py
src/onnx_inference_mqtt.py
node-red/flow.json
demo/result_images/
demo/result_video.mp4
README.md
```

## 13. README 작성 구조

```md
# On-device AIoT Driving Vision Mini Project

## 1. 문제 정의
무인 주행 시스템에서 카메라 입력을 이용해 사람, 차량, 장애물을 실시간 감지한다.

## 2. 시스템 구조
Camera -> YOLO -> ONNX Runtime -> MQTT -> Node-RED

## 3. 데이터
- 클래스
- 수집 방식
- 라벨링 방식

## 4. 모델
- 사용 모델
- 파인튜닝 조건
- 학습 결과

## 5. 성능
| Model | Size | mAP50 | CPU FPS | 비고 |
|---|---:|---:|---:|---|
| YOLOv8n Fine-tuned | | | | |
| ONNX Runtime | | | | |

## 6. MQTT 메시지
topic, payload 예시

## 7. Node-RED 대시보드
대시보드 캡처 및 설명

## 8. 온디바이스 적용 가능성
- 모델 크기
- 추론 속도
- Raspberry Pi/Jetson 적용 계획

## 9. 한계 및 개선 방향
- 데이터 수 부족
- 클래스 다양성 부족
- INT8 quantization
- 실제 보드 테스트
```

## 14. 팀빌딩 어필 문장

> YOLO 모델을 무인주행 위험 객체 감지 목적에 맞게 파인튜닝하고, ONNX로 변환하여 온디바이스 추론 가능성을 확인했습니다. 또한 MQTT와 Node-RED를 연동해 감지 결과를 AIoT 시스템에서 실시간으로 시각화하는 파이프라인을 구현했습니다. 공통 프로젝트에서는 카메라 기반 객체 인식 모델 개발, 경량화, 추론 속도 개선, 보드 탑재 검증 역할을 맡고 싶습니다.

## 15. 핵심 메시지

이 미니프로젝트의 핵심은 높은 정확도의 모델을 만드는 것이 아니라, **온디바이스 AIoT 무인주행 시스템에 필요한 전체 흐름을 작게 완성하는 것**이다.

따라서 우선순위는 다음과 같다.

```text
완성 가능한 파이프라인 > 높은 모델 성능 > 기능 확장
```
