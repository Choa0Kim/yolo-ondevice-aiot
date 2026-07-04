# 제조/물류 AMR 안전 주행 데이터셋 가이드

## 1. 도메인 정의

이 프로젝트는 스마트팩토리/물류창고에서 AMR이 주행 중 만날 수 있는 위험 객체를 카메라 기반으로 감지하는 것을 목표로 한다.

검증 목표는 실제 AMR 제어가 아니라, **AMR 안전 주행을 위한 온디바이스 비전 판단 모듈 프로토타입**을 만드는 것이다.

## 2. 확정 클래스

| ID | 클래스 | 의미 | 예시 |
|---:|---|---|---|
| 0 | `person` | 작업자 | 서 있는 사람, 걷는 사람, 통로 근처 사람 |
| 1 | `box` | 적재물/장애물 | 택배 상자, 박스 더미 |
| 2 | `traffic_cone` | 통제/주의 구역 | 안전콘, 라바콘 |
| 3 | `forklift` | 이동 장비 | 지게차, 소형 운반차 |

`vehicle` 대신 `forklift`를 우선 사용한다. 제조/물류 도메인 메시지가 더 분명하고, AMR 안전 주행 상황과 직접 연결되기 때문이다.

## 3. 데이터 수량 목표

하루 반 미니프로젝트 기준으로 과하게 큰 데이터셋을 만들지 않는다.

| 기준 | 목표 |
|---|---:|
| 최소 이미지 수 | 120장 |
| 권장 이미지 수 | 200-300장 |
| 클래스별 최소 | 30장 |
| 클래스별 권장 | 50-80장 |
| validation 비율 | 20% |

## 4. 수집 우선순위

### 1순위: 직접 재현 가능한 객체

- `person`: 직접 촬영 가능
- `box`: 택배 상자, 보관함 등으로 촬영 가능

### 2순위: 공개 이미지/영상 활용

- `traffic_cone`: 직접 구하기 어렵다면 공개 이미지 사용
- `forklift`: 직접 촬영이 어렵기 때문에 공개 이미지 또는 공개 영상 프레임 활용

### 직접 촬영이 어려운 경우의 대체 전략

직접 촬영이 어렵다면 공개 데이터셋과 공개 영상을 조합한다.

권장 우선순위:

1. **Roboflow Universe에서 YOLO 형식 데이터셋 검색**
   - 장점: YOLO format export가 쉬움
   - 검색어: `warehouse`, `forklift`, `traffic cone`, `box`, `pallet`, `worker`
   - 주의: 각 데이터셋의 라이선스와 출처를 README에 기록

2. **Open Images V7에서 필요한 클래스만 추출**
   - 장점: 대규모 bounding box 데이터셋
   - 활용 대상: `person`, `box` 계열, `traffic cone` 계열, `forklift` 계열 후보
   - 주의: 클래스명이 프로젝트 클래스와 정확히 일치하지 않을 수 있으므로 매핑 필요

3. **공개 물류창고/공장 영상에서 프레임 추출 후 직접 라벨링**
   - 장점: 실제 동영상 기반 실시간 검증과 잘 맞음
   - 방법: 짧은 공개 영상에서 1-2초 간격으로 프레임 추출
   - 주의: 영상 라이선스 확인 필요

4. **생성형 이미지 또는 합성 이미지 보조 활용**
   - 장점: 부족한 클래스 보완 가능
   - 주의: 실제 환경과 차이가 커질 수 있으므로 validation 데이터에는 과하게 넣지 않음

추천 조합:

```text
person        -> Open Images 또는 COCO 계열 공개 데이터
box           -> Open Images 또는 Roboflow Universe
traffic_cone  -> Roboflow Universe 또는 Open Images
forklift      -> Roboflow Universe 또는 공개 영상 프레임 직접 라벨링
```

현재 로컬 생성 방식:

```text
person, box
  -> Open Images V7
  -> scripts/prepare_openimages_person_box.py
  -> data/processed/openimages_person_box_yolo
```

현재 생성된 `person/box` 데이터는 `traffic_cone`, `forklift` 데이터와 병합되어 최종 학습 데이터셋에 포함되었다.

## 11. 데이터 출처 및 클래스 매핑

최종 데이터셋은 3개 출처의 데이터를 병합하여 구성한다.

| 출처 | URL | 라이선스 | 사용 클래스 | 최종 클래스 |
|---|---|---|---|---|
| Open Images V7 | https://storage.googleapis.com/openimages/web/index.html | Open Images 데이터셋 라이선스 | `Person`, `Box` | `person`, `box` |
| Roboflow FRC2023-935 v4 | https://universe.roboflow.com/mail-vanbergeijk/frc2023-935/dataset/4 | CC BY 4.0 | `cone` | `traffic_cone` |
| Roboflow Warehouse v1 | https://universe.roboflow.com/akademia-grniczo-hutnicza-im-stanisawa-staszica-w-krakowie/warehouse-0w7f0/dataset/1 | CC BY 4.0 | `box`, `forklift`, `person` | `box`, `forklift`, `person` |

최종 클래스 ID:

```text
0: person
1: box
2: traffic_cone
3: forklift
```

클래스 매핑:

```text
Open Images V7
  Person -> 0: person
  Box    -> 1: box

Roboflow FRC2023-935 v4
  cone   -> 2: traffic_cone

Roboflow Warehouse v1
  box      -> 1: box
  forklift -> 3: forklift
  person   -> 0: person
```

## 12. 중간 데이터셋 생성 결과

### Open Images person/box

생성 위치:

```text
data/processed/openimages_person_box_yolo
```

생성 결과:

```text
train: 100 images, 573 objects
  person: 314 objects
  box: 259 objects

val: 24 images, 99 objects
  person: 65 objects
  box: 34 objects
```

### Roboflow traffic_cone

원본 위치:

```text
data/processed/traffic_cone_yolo
```

정규화 위치:

```text
data/processed/traffic_cone_yolo_normalized
```

생성 결과:

```text
train: 573 images, 1521 objects
val: 49 images, 118 objects
```

### Roboflow forklift

원본 위치:

```text
data/processed/forklift_yolo
```

정규화 위치:

```text
data/processed/forklift_yolo_normalized
```

생성 결과:

```text
train: 140 images, 773 objects
val: 40 images, 178 objects
```

## 13. 최종 데이터셋 상태

최종 병합 데이터셋 위치:

```text
data/processed/dataset_final
```

최종 분포:

```text
train: 813 images, 813 labels
  person: 410 objects
  box: 857 objects
  traffic_cone: 1521 objects
  forklift: 79 objects

val: 113 images, 113 labels
  person: 91 objects
  box: 163 objects
  traffic_cone: 118 objects
  forklift: 23 objects
```

최종 `data.yaml`:

```yaml
path: .
train: images/train
val: images/val

names:
  0: person
  1: box
  2: traffic_cone
  3: forklift
```

주의사항:

- `traffic_cone` 객체 수가 가장 많고 `forklift` 객체 수가 가장 적다.
- 미니프로젝트 학습은 이 상태로 진행 가능하다.
- `forklift` 성능이 낮게 나오면 forklift 데이터를 추가 확보하거나 augmentation을 조정한다.
- 데이터 원본과 가공 데이터는 GitHub에 올리지 않는다.

검증 명령:

```powershell
python scripts/check_yolo_dataset.py data\processed\dataset_final
```

데이터 출처 기록 예시:

```md
## Dataset Sources

- Roboflow Universe: dataset name, URL, license
- Open Images V7: selected classes, license
- Public video frames: video URL, license, extracted frame count
```

## 5. 이미지 조건

다양한 조건을 일부러 섞어야 실시간 영상 검증에서 덜 흔들린다.

- 정면, 측면, 사선 시점
- 가까운 객체, 먼 객체
- 객체 일부가 잘린 이미지
- 밝은 환경, 어두운 환경
- 통로 중앙 객체, 통로 가장자리 객체
- 여러 객체가 동시에 있는 이미지

## 6. 라벨링 기준

### 공통 기준

- 보이는 객체 영역을 최대한 타이트하게 bounding box로 감싼다.
- 객체가 일부만 보여도 식별 가능하면 라벨링한다.
- 너무 작아서 식별이 어려운 객체는 라벨링하지 않는다.
- 그림자, 반사, 포스터 속 객체는 라벨링하지 않는다.

### 클래스별 기준

| 클래스 | 라벨링 기준 |
|---|---|
| `person` | 전신이 아니어도 작업자로 식별 가능하면 라벨링 |
| `box` | 단일 박스 또는 박스 더미를 하나의 장애물로 라벨링 |
| `traffic_cone` | 콘 본체가 보이면 라벨링 |
| `forklift` | 지게차 전체 또는 명확한 일부가 보이면 라벨링 |

## 7. 폴더 구조

YOLO 학습용 구조는 다음과 같이 맞춘다.

```text
data/
  images/
    train/
    val/
  labels/
    train/
    val/
  data.yaml
```

이미지와 라벨 파일 이름은 확장자만 다르게 맞춘다.

```text
images/train/warehouse_001.jpg
labels/train/warehouse_001.txt
```

## 8. 검증 데이터 분리

학습에 사용하지 않은 이미지를 validation/test 용도로 반드시 남긴다.

권장:

- train: 80%
- val: 20%

주의:

- 같은 동영상에서 연속으로 추출한 프레임은 train과 val에 섞지 않는다.
- 거의 같은 이미지가 train과 val에 동시에 들어가면 성능이 과대평가된다.

## 9. 실시간 시스템 검증용 동영상

실시간 검증은 사진 성능 평가와 별도로 진행한다.

입력 예시:

```text
demo/input/warehouse_test.mp4
```

동영상에는 다음 상황이 포함되면 좋다.

- 사람이 화면 중앙으로 진입
- 박스가 화면 하단 주행 경로에 위치
- 콘 또는 지게차가 화면 중간에 등장
- 객체가 사라지며 위험도가 `STOP` 또는 `SLOW`에서 `GO`로 바뀌는 장면

## 10. GitHub 업로드 원칙

다음 파일은 GitHub에 올리지 않는다.

- 원본 이미지
- 라벨 파일 전체
- 학습된 모델 파일
- 원본/결과 동영상
- 개인정보가 포함된 참고자료

GitHub에는 다음만 기록한다.

- 데이터셋 구성 설명
- 클래스 정의
- 라벨링 기준
- 샘플 결과 이미지 일부
- 실행 방법
