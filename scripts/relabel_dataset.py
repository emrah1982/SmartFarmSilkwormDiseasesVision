"""
Dataset sınıf etiketlerini yeniden adlandırma scripti.

Usage:
    python scripts/relabel_dataset.py --input datasets/roboflow --output datasets/processed
"""

import argparse
import logging
import os
import shutil
import yaml
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


CLASS_MAPPING = {
    "ripe": "strawberry_ripe",
    "semi-ripe": "strawberry_semi_ripe",
    "semi_ripe": "strawberry_semi_ripe",
    "unripe": "strawberry_unripe",
    "green": "strawberry_unripe",
    "strawberry": "strawberry_ripe",
}


def load_data_yaml(yaml_path: str) -> Dict:
    """data.yaml dosyasını yükler."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"YAML yükleme hatası: {e}")
        return {}


def create_class_id_mapping(old_names: Dict[int, str]) -> Dict[int, int]:
    """Eski sınıf ID'lerini yeni ID'lere eşler.
    
    Args:
        old_names: Eski sınıf isimleri {id: name}
        
    Returns:
        Mapping {old_id: new_id}
    """
    new_names = {
        0: "strawberry_ripe",
        1: "strawberry_semi_ripe",
        2: "strawberry_unripe",
    }
    
    id_mapping = {}
    for old_id, old_name in old_names.items():
        mapped_name = CLASS_MAPPING.get(old_name.lower(), "strawberry_ripe")
        
        for new_id, new_name in new_names.items():
            if mapped_name == new_name:
                id_mapping[old_id] = new_id
                break
    
    return id_mapping


def relabel_txt_file(txt_path: str, id_mapping: Dict[int, int]) -> int:
    """Tek bir label dosyasını yeniden etiketler.
    
    Args:
        txt_path: Label dosya yolu
        id_mapping: Sınıf ID mapping
        
    Returns:
        Güncellenen satır sayısı
    """
    try:
        with open(txt_path, 'r') as f:
            lines = f.readlines()
        
        updated_lines = []
        count = 0
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                old_class_id = int(parts[0])
                new_class_id = id_mapping.get(old_class_id, old_class_id)
                
                if new_class_id != old_class_id:
                    count += 1
                
                parts[0] = str(new_class_id)
                updated_lines.append(' '.join(parts) + '\n')
            else:
                updated_lines.append(line)
        
        with open(txt_path, 'w') as f:
            f.writelines(updated_lines)
        
        return count
    except Exception as e:
        logger.error(f"Label dosyası güncelleme hatası {txt_path}: {e}")
        return 0


def relabel_dataset(input_dir: str, output_dir: str) -> bool:
    """Dataset'i yeniden etiketler.
    
    Args:
        input_dir: Kaynak dataset dizini
        output_dir: Hedef dataset dizini
        
    Returns:
        Başarılı ise True
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    yaml_path = input_path / "data.yaml"
    if not yaml_path.exists():
        logger.error(f"data.yaml bulunamadı: {yaml_path}")
        return False
    
    data_config = load_data_yaml(str(yaml_path))
    old_names = data_config.get('names', {})
    
    if isinstance(old_names, list):
        old_names = {i: name for i, name in enumerate(old_names)}
    
    logger.info(f"Eski sınıflar: {old_names}")
    
    id_mapping = create_class_id_mapping(old_names)
    logger.info(f"Sınıf ID mapping: {id_mapping}")
    
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
        
        logger.info(f"İşleniyor: {split}")
        
        for img_file in images_src.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                shutil.copy2(img_file, images_dst / img_file.name)
        
        total_updated = 0
        label_count = 0
        
        if labels_src.exists():
            for label_file in labels_src.glob('*.txt'):
                dst_label = labels_dst / label_file.name
                shutil.copy2(label_file, dst_label)
                
                updated = relabel_txt_file(str(dst_label), id_mapping)
                total_updated += updated
                label_count += 1
        
        logger.info(f"  {split}: {label_count} label dosyası, {total_updated} satır güncellendi")
    
    new_data_yaml = {
        'path': str(output_path.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 3,
        'names': {
            0: 'strawberry_ripe',
            1: 'strawberry_semi_ripe',
            2: 'strawberry_unripe',
        }
    }
    
    with open(output_path / 'data.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(new_data_yaml, f, default_flow_style=False, allow_unicode=True)
    
    logger.info(f"Yeni data.yaml oluşturuldu: {output_path / 'data.yaml'}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Dataset sınıf etiketlerini yeniden adlandır")
    parser.add_argument("--input", type=str, required=True, help="Kaynak dataset dizini")
    parser.add_argument("--output", type=str, required=True, help="Hedef dataset dizini")
    
    args = parser.parse_args()
    
    success = relabel_dataset(args.input, args.output)
    
    if success:
        logger.info("✅ Dataset başarıyla yeniden etiketlendi!")
        logger.info(f"📁 Konum: {args.output}")
        logger.info("📝 Sonraki adım: python scripts/train_yolo.py")
    else:
        logger.error("❌ Dataset yeniden etiketlenemedi!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
