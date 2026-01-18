# Kullanım Kılavuzu (Strawberry Vision)

## Kurulum

```
pip install -r requirements.txt
```

## Çalıştırma

- Tek görsel:
```
python -m strawberry_vision.main --image sample.jpg
```

- Video:
```
python -m strawberry_vision.main --video path/to/video.mp4 --max-frames 200
```

- YOLO modeli ile (opsiyonel):
```
python -m strawberry_vision.main --image sample.jpg --model path/to/best.pt
```

Not: Model verilmezse dedektör dummy modda çalışır ve boş sonuç döndürebilir.

## Proje Yapısı

```
strawberry_vision/
  application/
    pipeline.py
  domain/
    entities.py
    services.py
  infrastructure/
    detectors.py
    sources.py
  presentation/
    visualizer.py
  main.py
```

## Colab Kullanımı

- `strawberry_vision` klasörünü zipleyip Colab'e yükleyin.
- Bağımlılıklar:
```
!pip install ultralytics opencv-python numpy matplotlib
```
- Örnek çalıştırma:
```python
from strawberry_vision.main import main
import sys

sys.argv = ["", "--image", "sample.jpg"]
main()
```

## Smoke Test

```
python tests/smoke_test.py
```

Bu test, sahte bir dedektör ile pipeline'ın sayım akışını hızlıca doğrular.
