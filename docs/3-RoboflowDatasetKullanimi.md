# 🍓 Roboflow Dataset Kullanımı ve Eğitim Kılavuzu

## 📦 Önerilen Roboflow Dataset Linkleri

### 1. Strawberry Detection Dataset (Temel)
- **Link**: https://universe.roboflow.com/strawberry-detection/strawberry-detection-dataset
- **Sınıflar**: strawberry
- **Görüntü Sayısı**: ~500-1000
- **Kullanım**: Temel çilek tespiti için

### 2. Strawberry Ripeness Classification
- **Link**: https://universe.roboflow.com/fruit-detection/strawberry-ripeness
- **Sınıflar**: ripe, unripe, semi-ripe
- **Görüntü Sayısı**: ~800+
- **Kullanım**: Olgunluk sınıflandırması için ideal

### 3. Fruit Detection - Strawberry
- **Link**: https://universe.roboflow.com/object-detection/fruit-detection-strawberry
- **Sınıflar**: strawberry (çeşitli olgunluk durumları)
- **Görüntü Sayısı**: ~1200+
- **Kullanım**: Geniş veri çeşitliliği

### 4. Agricultural Strawberry Dataset
- **Link**: https://universe.roboflow.com/agriculture/strawberry-field-detection
- **Sınıflar**: strawberry_ripe, strawberry_unripe
- **Görüntü Sayısı**: ~600+
- **Kullanım**: Tarla koşullarında eğitim

## 🎯 Roboflow Kullanım İpuçları

### Dataset İndirme
```bash
# Roboflow API ile indirme
pip install roboflow

# Python script ile
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("workspace-name").project("project-name")
dataset = project.version(1).download("yolov8")
```

### Export Formatı
- ✅ **YOLOv8** formatını seç (PyTorch)
- ✅ **Train/Val/Test** split: 70/20/10 veya 80/15/5
- ✅ **Preprocessing**: Auto-Orient, Resize (640x640)
- ✅ **Augmentation**: Roboflow'da veya kod içinde

### Sınıf Adı Standardizasyonu
Roboflow'dan indirilen datasette sınıf adları farklı olabilir. Bizim projede kullanılacak standart:
- `strawberry_ripe` → Olgun çilek
- `strawberry_semi_ripe` → Yarı olgun çilek
- `strawberry_unripe` → Olgun olmayan çilek

## 🔄 Sınıf Yeniden Etiketleme Stratejisi

### 1. Otomatik Mapping
Roboflow'dan gelen sınıfları otomatik olarak bizim standarda çevir:

```python
CLASS_MAPPING = {
    "ripe": "strawberry_ripe",
    "semi-ripe": "strawberry_semi_ripe",
    "semi_ripe": "strawberry_semi_ripe",
    "unripe": "strawberry_unripe",
    "green": "strawberry_unripe",
    "strawberry": "strawberry_ripe",  # Varsayılan
}
```

### 2. Label Dosyası Güncelleme
YOLO formatındaki `.txt` dosyalarında sınıf ID'lerini güncelle:
- Eski: `0 0.5 0.5 0.1 0.1` (class_id x_center y_center width height)
- Yeni: Mapping'e göre class_id'yi değiştir

### 3. data.yaml Güncelleme
```yaml
names:
  0: strawberry_ripe
  1: strawberry_semi_ripe
  2: strawberry_unripe
```

## 🎨 Augmentation Stratejisi

### Roboflow Augmentation (Online)
Dataset export ederken Roboflow'da uygula:
- **Flip**: Horizontal (50%)
- **Rotation**: ±15°
- **Brightness**: ±20%
- **Exposure**: ±15%
- **Blur**: Up to 1px
- **Noise**: Up to 2%

### YOLOv8 Augmentation (Training Time)
`data.yaml` veya training script'te:
```yaml
# Augmentation hyperparameters
hsv_h: 0.015  # Hue augmentation
hsv_s: 0.7    # Saturation augmentation
hsv_v: 0.4    # Value (brightness) augmentation
degrees: 10.0  # Rotation
translate: 0.1 # Translation
scale: 0.5     # Scale
shear: 0.0     # Shear
perspective: 0.0 # Perspective
flipud: 0.0    # Flip up-down
fliplr: 0.5    # Flip left-right
mosaic: 1.0    # Mosaic augmentation
mixup: 0.1     # Mixup augmentation
```

### Özel Augmentation (Kod İçinde)
Albumentations kullanarak:
```python
import albumentations as A

transform = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=20, p=0.5),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
    A.GaussianBlur(blur_limit=3, p=0.3),
    A.RandomRotate90(p=0.5),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
```

## 📊 Dataset Split Stratejisi

### Dengeli Split
```python
# Olgunluk durumuna göre stratified split
from sklearn.model_selection import train_test_split

# Her sınıftan eşit oranda train/val/test'e dağıt
train_ratio = 0.70
val_ratio = 0.20
test_ratio = 0.10
```

### Minimum Görüntü Sayısı
- **Train**: En az 500 görüntü
- **Validation**: En az 100 görüntü
- **Test**: En az 50 görüntü

Her sınıf için minimum:
- `strawberry_ripe`: 200+ görüntü
- `strawberry_semi_ripe`: 150+ görüntü
- `strawberry_unripe`: 150+ görüntü

## 🔧 YOLOv8 Config Yapısı

### data.yaml (Dataset Config)
```yaml
path: /path/to/dataset  # Dataset root
train: images/train     # Train images
val: images/val         # Validation images
test: images/test       # Test images (optional)

nc: 3  # Number of classes
names:
  0: strawberry_ripe
  1: strawberry_semi_ripe
  2: strawberry_unripe
```

### Eğitim Parametreleri
```yaml
# Model
model: yolov8n.pt  # veya yolov8s.pt, yolov8m.pt

# Training
epochs: 100
batch: 16
imgsz: 640
device: 0  # GPU ID veya 'cpu'

# Optimizer
optimizer: AdamW
lr0: 0.01
lrf: 0.01
momentum: 0.937
weight_decay: 0.0005

# Loss
box: 7.5
cls: 0.5
dfl: 1.5
```

## 📝 Kullanım Adımları

### 1. Dataset İndirme
```bash
# Roboflow'dan YOLOv8 formatında indir
python scripts/download_dataset.py --api-key YOUR_KEY --workspace strawberry --project ripeness
```

### 2. Sınıf Yeniden Etiketleme
```bash
# Label dosyalarını güncelle
python scripts/relabel_dataset.py --input datasets/roboflow --output datasets/processed
```

### 3. Augmentation Uygulama
```bash
# Ek augmentation (opsiyonel)
python scripts/augment_dataset.py --input datasets/processed --output datasets/augmented --factor 2
```

### 4. Eğitim
```bash
# YOLOv8 eğitimi
python scripts/train_yolo.py --data configs/strawberry_data.yaml --config configs/train_config.yaml
```

## 🎓 Best Practices

### Dataset Kalitesi
- ✅ Farklı aydınlatma koşulları
- ✅ Farklı açılar ve mesafeler
- ✅ Farklı arka planlar
- ✅ Çeşitli olgunluk aşamaları
- ✅ Kısmi görünürlük (occlusion) örnekleri

### Etiketleme Kalitesi
- ✅ Bounding box tam çileği kapsasın
- ✅ Olgunluk sınıflandırması tutarlı olsun
- ✅ Belirsiz örnekleri işaretle veya çıkar
- ✅ Çok küçük çilekleri (<10px) filtrele

### Eğitim İzleme
- ✅ TensorBoard ile metrikleri takip et
- ✅ Validation loss'u kontrol et (overfitting)
- ✅ mAP@0.5 ve mAP@0.5:0.95 metriklerini izle
- ✅ Her 10 epoch'ta checkpoint kaydet

## 🔗 Faydalı Linkler

- **Roboflow Universe**: https://universe.roboflow.com
- **YOLOv8 Docs**: https://docs.ultralytics.com
- **Augmentation Guide**: https://albumentations.ai/docs/
- **YOLO Format**: https://roboflow.com/formats/yolov8-pytorch-txt

## 📞 Destek

Dataset veya eğitim ile ilgili sorunlar için:
- `docs/2-YOLOegitimiHiperparametre.md` - Detaylı eğitim kılavuzu
- `docs/2.2-ModelHataAnaliziIyilestirmePromptu.md` - Hata analizi
- `scripts/train_yolo.py` - Eğitim script'i
