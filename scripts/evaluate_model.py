"""
Eğitilmiş YOLO26 modelini değerlendirme scripti.

Usage:
    python scripts/evaluate_model.py --model runs/train/yolo26/weights/best.pt --data configs/silkworm_data.yaml
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def evaluate_model(model_path: str, data_yaml: str, split: str = 'val') -> bool:
    """Modeli değerlendirir.
    
    Args:
        model_path: Model dosya yolu (.pt)
        data_yaml: Dataset config dosyası
        split: Değerlendirme split'i ('val' veya 'test')
        
    Returns:
        Başarılı ise True
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("Ultralytics yüklü değil. 'pip install ultralytics' ile yükleyin.")
        return False
    
    try:
        logger.info(f"Model yükleniyor: {model_path}")
        model = YOLO(model_path)
        
        logger.info(f"Değerlendirme başlıyor: {split} split")
        results = model.val(data=data_yaml, split=split)
        
        logger.info("Değerlendirme tamamlandı!")
        
        metrics = results.results_dict if hasattr(results, 'results_dict') else {}
        
        logger.info("\n" + "="*50)
        logger.info("DEĞERLENDIRME SONUÇLARI")
        logger.info("="*50)
        
        if metrics:
            logger.info(f"mAP@0.5: {metrics.get('metrics/mAP50(B)', 'N/A'):.4f}")
            logger.info(f"mAP@0.5:0.95: {metrics.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
            logger.info(f"Precision: {metrics.get('metrics/precision(B)', 'N/A'):.4f}")
            logger.info(f"Recall: {metrics.get('metrics/recall(B)', 'N/A'):.4f}")
        
        if hasattr(results, 'box'):
            box_metrics = results.box
            if hasattr(box_metrics, 'maps'):
                logger.info("\nSınıf Bazlı mAP@0.5:")
                for i, map_val in enumerate(box_metrics.maps):
                    logger.info(f"  Sınıf {i}: {map_val:.4f}")
        
        logger.info("="*50 + "\n")
        
        return True
    except Exception as e:
        logger.error(f"Değerlendirme hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="YOLO26 model değerlendirme")
    parser.add_argument("--model", type=str, required=True, help="Model dosyası (.pt)")
    parser.add_argument("--data", type=str, required=True, help="Dataset YAML dosyası")
    parser.add_argument("--split", type=str, default='val', choices=['val', 'test'], help="Değerlendirme split'i")
    
    args = parser.parse_args()
    
    if not Path(args.model).exists():
        logger.error(f"Model bulunamadı: {args.model}")
        return 1
    
    success = evaluate_model(args.model, args.data, args.split)
    
    if success:
        logger.info("✅ Değerlendirme başarıyla tamamlandı!")
    else:
        logger.error("❌ Değerlendirme başarısız!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
