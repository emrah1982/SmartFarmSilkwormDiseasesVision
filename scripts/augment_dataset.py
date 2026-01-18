"""
Dataset augmentation scripti (Albumentations kullanarak).

Usage:
    python scripts/augment_dataset.py --input datasets/processed --output datasets/augmented --factor 2
"""

import argparse
import logging
import os
import shutil
import yaml
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_augmentation_config(config_path: str = "configs/augmentation_config.yaml"):
    """Augmentation config dosyasını yükler."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Config yüklenemedi, varsayılan kullanılacak: {e}")
        return None


def create_augmentation_pipeline():
    """Albumentations augmentation pipeline oluşturur."""
    try:
        import albumentations as A
    except ImportError:
        logger.error("Albumentations yüklü değil. 'pip install albumentations' ile yükleyin.")
        return None
    
    transform = A.Compose([
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=20, p=0.5),
        A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=0.3),
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
        A.GaussianBlur(blur_limit=(3, 5), p=0.3),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.15, rotate_limit=15, border_mode=0, p=0.5),
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
    
    return transform


def read_yolo_labels(label_path: str) -> Tuple[List[List[float]], List[int]]:
    """YOLO format label dosyasını okur.
    
    Returns:
        (bboxes, class_labels) - bboxes: [[x_center, y_center, width, height], ...]
    """
    bboxes = []
    class_labels = []
    
    try:
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    bbox = [float(x) for x in parts[1:5]]
                    class_labels.append(class_id)
                    bboxes.append(bbox)
    except Exception as e:
        logger.error(f"Label okuma hatası {label_path}: {e}")
    
    return bboxes, class_labels


def write_yolo_labels(label_path: str, bboxes: List[List[float]], class_labels: List[int]):
    """YOLO format label dosyası yazar."""
    try:
        with open(label_path, 'w') as f:
            for bbox, class_id in zip(bboxes, class_labels):
                line = f"{class_id} {' '.join(map(str, bbox))}\n"
                f.write(line)
    except Exception as e:
        logger.error(f"Label yazma hatası {label_path}: {e}")


def augment_image(image_path: str, label_path: str, output_image_path: str, 
                  output_label_path: str, transform) -> bool:
    """Tek bir görüntüyü augment eder.
    
    Returns:
        Başarılı ise True
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Görüntü okunamadı: {image_path}")
            return False
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        bboxes, class_labels = read_yolo_labels(label_path)
        
        if len(bboxes) == 0:
            shutil.copy2(image_path, output_image_path)
            shutil.copy2(label_path, output_label_path)
            return True
        
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)
        
        aug_image = cv2.cvtColor(transformed['image'], cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_image_path, aug_image)
        
        write_yolo_labels(output_label_path, transformed['bboxes'], transformed['class_labels'])
        
        return True
    except Exception as e:
        logger.error(f"Augmentation hatası {image_path}: {e}")
        return False


def augment_dataset(input_dir: str, output_dir: str, factor: int = 2) -> bool:
    """Dataset'i augment eder.
    
    Args:
        input_dir: Kaynak dataset dizini
        output_dir: Hedef dataset dizini
        factor: Her görüntü için kaç augmented versiyon oluşturulacak
        
    Returns:
        Başarılı ise True
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    transform = create_augmentation_pipeline()
    if transform is None:
        return False
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    for split in ['train', 'val', 'test']:
        images_src = input_path / 'images' / split
        labels_src = input_path / 'labels' / split
        
        if not images_src.exists():
            logger.warning(f"Split bulunamadı: {split}")
            continue
        
        images_dst = output_path / 'images' / split
        labels_dst = output_path / 'labels' / split
        
        images_dst.mkdir(parents=True, exist_ok=True)
        labels_dst.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Augmenting: {split}")
        
        image_files = list(images_src.glob('*'))
        total = len(image_files)
        success_count = 0
        
        for idx, img_file in enumerate(image_files):
            if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                continue
            
            label_file = labels_src / f"{img_file.stem}.txt"
            if not label_file.exists():
                logger.warning(f"Label bulunamadı: {label_file}")
                continue
            
            shutil.copy2(img_file, images_dst / img_file.name)
            shutil.copy2(label_file, labels_dst / label_file.name)
            
            for aug_idx in range(factor):
                aug_img_name = f"{img_file.stem}_aug{aug_idx}{img_file.suffix}"
                aug_label_name = f"{img_file.stem}_aug{aug_idx}.txt"
                
                success = augment_image(
                    str(img_file),
                    str(label_file),
                    str(images_dst / aug_img_name),
                    str(labels_dst / aug_label_name),
                    transform
                )
                
                if success:
                    success_count += 1
            
            if (idx + 1) % 50 == 0:
                logger.info(f"  İşlenen: {idx + 1}/{total}")
        
        logger.info(f"  {split}: {total} orijinal, {success_count} augmented görüntü oluşturuldu")
    
    data_yaml_src = input_path / 'data.yaml'
    if data_yaml_src.exists():
        shutil.copy2(data_yaml_src, output_path / 'data.yaml')
        
        with open(output_path / 'data.yaml', 'r') as f:
            data_config = yaml.safe_load(f)
        
        data_config['path'] = str(output_path.absolute())
        
        with open(output_path / 'data.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Dataset augmentation")
    parser.add_argument("--input", type=str, required=True, help="Kaynak dataset dizini")
    parser.add_argument("--output", type=str, required=True, help="Hedef dataset dizini")
    parser.add_argument("--factor", type=int, default=2, help="Augmentation faktörü")
    
    args = parser.parse_args()
    
    success = augment_dataset(args.input, args.output, args.factor)
    
    if success:
        logger.info("✅ Dataset başarıyla augment edildi!")
        logger.info(f"📁 Konum: {args.output}")
        logger.info("📝 Sonraki adım: python scripts/train_yolo.py")
    else:
        logger.error("❌ Dataset augment edilemedi!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
