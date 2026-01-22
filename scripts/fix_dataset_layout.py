"""
Dataset klasör düzeni onarım scripti.

Amaç: YOLOv8'in beklediği klasör yapısını garanti altına almak.
Beklenen yapı:
root/
  - train/
      images/
      labels/
  - val/ veya valid/
      images/
      labels/
  - test/ (opsiyonel)
      images/
      labels/
  - data.yaml

Kullanım (Colab veya lokal):
  python scripts/fix_dataset_layout.py --root "/content/drive/MyDrive/StrawberryVision/dataset"

Notlar:
- Eğer 'valid' klasörü varsa ve data.yaml ona işaret ediyorsa, isim değiştirmiyoruz; sadece alt klasörleri oluşturuyoruz.
- images uzantıları: .jpg, .jpeg, .png, .bmp, .webp
- labels uzantısı: .txt (YOLO formatı)
"""

import argparse
import logging
from pathlib import Path
from typing import Iterable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
LABEL_EXTS = {".txt"}


def ensure_split_structure(split_dir: Path) -> None:
    if not split_dir.exists():
        return

    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"

    if images_dir.exists() and labels_dir.exists():
        logger.info(f"OK: {split_dir.name}/images ve labels mevcut")
        return

    # images/labels yoksa oluştur ve dosyaları ayır
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    moved_images = 0
    moved_labels = 0

    # split_dir içindeki (images/labels hariç) tüm dosya ve alt klasörleri tara
    for p in split_dir.rglob('*'):
        if not p.is_file():
            continue
        # 'images'/'labels' altındaki dosyalar zaten doğru yerde
        try:
            rel = p.relative_to(split_dir)
            if any(part in {"images", "labels"} for part in rel.parts):
                continue
        except Exception:
            pass
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS:
            dest = images_dir / p.name
            try:
                p.rename(dest)
                moved_images += 1
            except Exception:
                # Aynı isim varsa üzerine yazma; atla
                pass
        elif ext in LABEL_EXTS:
            dest = labels_dir / p.name
            try:
                p.rename(dest)
                moved_labels += 1
            except Exception:
                pass

    logger.info(f"{split_dir.name}: taşınan images={moved_images}, labels={moved_labels}")


def main() -> int:
    ap = argparse.ArgumentParser(description="YOLOv8 dataset klasör düzeni onarımı")
    ap.add_argument("--root", type=str, required=True, help="Dataset kök dizini (data.yaml ile aynı seviyede)")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        logger.error(f"Kök dizin bulunamadı: {root}")
        return 1

    logger.info(f"Dataset kökü: {root}")

    # train
    ensure_split_structure(root / "train")
    # val ve/veya valid
    ensure_split_structure(root / "val")
    ensure_split_structure(root / "valid")
    # test
    ensure_split_structure(root / "test")

    logger.info("Tamamlandı. Gerekli klasörler oluşturuldu ve dosyalar yerleştirildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
