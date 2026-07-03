# Data

이 폴더에는 YOLO 학습용 데이터셋 구조와 데이터 설명을 둡니다.

대용량 이미지와 라벨 파일은 GitHub에 직접 올리지 않습니다.

권장 구조:

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

초기 클래스:

```yaml
names:
  0: person
  1: box
  2: traffic_cone
  3: forklift
```

라벨링 기준과 데이터 수집 기준은 [docs/dataset_guide.md](../docs/dataset_guide.md)를 참고합니다.

Colab 학습 시에는 `data.yaml.example`을 복사하여 실제 경로에 맞게 `data.yaml`로 수정합니다.
