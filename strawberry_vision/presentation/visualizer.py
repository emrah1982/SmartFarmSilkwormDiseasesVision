from typing import List, Tuple
import logging
import os

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

logger = logging.getLogger(__name__)


class Visualizer:
    """Görselleştirme servisi.
    
    Tespit edilen çilekleri bounding box ve etiketlerle çizer.
    """
    
    def __init__(self, show_id: bool = True, show_confidence: bool = True):
        self.show_id = show_id
        self.show_confidence = show_confidence
        self._color_map = {
            "ripe": (0, 255, 0),      # Yeşil
            "semi_ripe": (0, 165, 255),  # Turuncu
            "unripe": (0, 0, 255),    # Kırmızı
        }

    def draw(self, frame, strawberries: List["Strawberry"]):
        """Çilekleri frame üzerine çizer.
        
        Args:
            frame: Görüntü frame'i
            strawberries: Çilek listesi
            
        Returns:
            Çizilmiş frame
        """
        if cv2 is None or frame is None:
            return frame
        
        for s in strawberries:
            x, y, w, h = s.detection.bbox
            color = self._color_map.get(s.ripeness.value, (255, 255, 255))
            
            # Bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Label
            label_parts = [s.ripeness.value]
            if self.show_confidence:
                label_parts.append(f"{s.detection.score:.2f}")
            if self.show_id and s.is_tracked():
                label_parts.append(f"ID:{s.id}")
            
            label = " ".join(label_parts)
            
            # Label background
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), color, -1)
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def save_frame(self, frame, output_path: str) -> bool:
        """Frame'i dosyaya kaydeder.
        
        Args:
            frame: Kaydedilecek frame
            output_path: Çıktı dosya yolu
            
        Returns:
            Başarılı ise True
        """
        if cv2 is None or frame is None:
            logger.error("Cannot save frame: OpenCV not available or frame is None")
            return False
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            success = cv2.imwrite(output_path, frame)
            if success:
                logger.info(f"Frame saved: {output_path}")
            else:
                logger.error(f"Failed to save frame: {output_path}")
            return success
        except Exception as e:
            logger.error(f"Error saving frame to {output_path}: {e}")
            return False
    
    def add_summary_overlay(self, frame, counts: dict, total: int) -> None:
        """Frame'e özet bilgi overlay'i ekler.
        
        Args:
            frame: Görüntü frame'i
            counts: Olgunluk sayımları
            total: Toplam çilek sayısı
        """
        if cv2 is None or frame is None:
            return
        
        y_offset = 30
        cv2.putText(frame, f"Total: {total}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        y_offset += 30
        for ripeness, count in counts.items():
            color = self._color_map.get(ripeness, (255, 255, 255))
            text = f"{ripeness}: {count}"
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 25
