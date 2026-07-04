# Colab 학습 및 ONNX 변환 가이드

## 1. 목적

로컬에서 생성한 `dataset_final.zip`을 Google Drive에 업로드한 뒤, Colab T4에서 YOLOv8n 모델을 학습하고 ONNX로 변환한다.

이 문서는 다음 과정을 재현하기 위한 실행 절차를 정리한다.

```text
Drive mount
-> dataset_final.zip 압축 해제
-> data.yaml 경로 수정
-> 1 epoch debug train
-> 30 epoch train
-> validation 이미지 예측
-> best.pt -> best.onnx 변환
-> 결과물 Drive 저장
```

## 2. Colab 런타임 설정

```text
런타임 -> 런타임 유형 변경 -> GPU -> T4
```

## 3. Drive 마운트

```python
from google.colab import drive
drive.mount("/content/drive")
```

## 4. 데이터셋 압축 해제

```python
zip_path = "/content/drive/MyDrive/ssafy_15/2학기/AIoT 미니플젝/dataset_final.zip"
extract_dir = "/content/dataset_final"

!rm -rf "$extract_dir"
!mkdir -p "$extract_dir"
!unzip -q "$zip_path" -d "$extract_dir"
```

구조 확인:

```python
!find /content/dataset_final/images/train -name "*.jpg" | wc -l
!find /content/dataset_final/images/val -name "*.jpg" | wc -l
!find /content/dataset_final/labels/train -name "*.txt" | wc -l
!find /content/dataset_final/labels/val -name "*.txt" | wc -l
!cat /content/dataset_final/data.yaml
```

기대값:

```text
train images: 813
val images: 113
train labels: 813
val labels: 113
```

## 5. data.yaml 경로 수정

압축 파일 안의 `data.yaml`은 로컬 기준으로 `path: .`를 사용한다. Colab 학습에서는 절대경로로 수정한다.

```python
data_yaml = """
path: /content/dataset_final
train: images/train
val: images/val

names:
  0: person
  1: box
  2: traffic_cone
  3: forklift
"""

with open("/content/dataset_final/data.yaml", "w") as f:
    f.write(data_yaml)
```

## 6. 패키지 설치

```python
!pip install -q ultralytics onnx onnxruntime
```

## 7. 1 epoch 디버그 학습

데이터 구조와 학습 파이프라인이 정상인지 먼저 확인한다.

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="/content/dataset_final/data.yaml",
    epochs=1,
    imgsz=640,
    batch=8,
    project="/content/runs",
    name="debug_train_1epoch"
)
```

결과 확인:

```python
!ls -al /content/runs/debug_train_1epoch/weights
```

정상이라면 다음 파일이 생성된다.

```text
best.pt
last.pt
```

## 8. 본 학습

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="/content/dataset_final/data.yaml",
    epochs=30,
    imgsz=640,
    batch=8,
    project="/content/runs",
    name="logistics_yolov8n"
)
```

학습 완료 후 `logistics_yolov8n` 폴더 전체를 Google Drive에 복사한다.

보관해야 할 핵심 파일:

```text
runs/logistics_yolov8n/
  weights/
    best.pt
    last.pt
  args.yaml
  results.csv
  results.png
  confusion_matrix.png
  confusion_matrix_normalized.png
```

## 9. Validation 이미지 예측

```python
from ultralytics import YOLO

best_pt = "/content/drive/MyDrive/ssafy_15/2학기/AIoT 미니플젝/runs/logistics_yolov8n/weights/best.pt"
model = YOLO(best_pt)

model.predict(
    source="/content/dataset_final/images/val",
    imgsz=640,
    conf=0.25,
    save=True,
    project="/content/runs",
    name="val_predictions"
)
```

눈으로 확인할 항목:

```text
person이 person으로 나오는지
box가 box로 나오는지
traffic_cone이 traffic_cone으로 나오는지
forklift가 forklift로 나오는지
bbox가 객체를 제대로 감싸는지
```

결과를 Drive에 복사:

```python
!cp -r /content/runs/val_predictions "/content/drive/MyDrive/ssafy_15/2학기/AIoT 미니플젝/runs/val_predictions"
```

## 10. ONNX 변환

```python
from ultralytics import YOLO

best_pt = "/content/drive/MyDrive/ssafy_15/2학기/AIoT 미니플젝/runs/logistics_yolov8n/weights/best.pt"
model = YOLO(best_pt)
model.export(format="onnx", imgsz=640)
```

결과:

```text
runs/logistics_yolov8n/weights/best.onnx
```

## 11. 최종 성능 기록

학습 결과:

```text
Precision(B): 0.87
Recall(B): 0.72
mAP50(B): 0.79
mAP50-95(B): 0.56
```

성능 해석은 [model_evaluation.md](model_evaluation.md)를 참고한다.

