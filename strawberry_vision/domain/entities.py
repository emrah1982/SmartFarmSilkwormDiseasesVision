from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class Ripeness(Enum):
    """Çilek olgunluk durumu sınıflandırması.
    
    RIPE: Olgun (kırmızı renk baskın, hasada hazır)
    SEMI_RIPE: Yarı olgun (kırmızı-beyaz karışımı)
    UNRIPE: Olgun değil (yeşil veya açık beyaz)
    """
    RIPE = "ripe"
    SEMI_RIPE = "semi_ripe"
    UNRIPE = "unripe"

    @classmethod
    def from_string(cls, value: str) -> "Ripeness":
        """String değerden Ripeness enum'u oluşturur."""
        mapping = {"ripe": cls.RIPE, "semi_ripe": cls.SEMI_RIPE, "unripe": cls.UNRIPE}
        return mapping.get(value.lower(), cls.UNRIPE)


@dataclass
class Detection:
    """Nesne tespit sonucu.
    
    Attributes:
        bbox: Bounding box (x, y, width, height)
        score: Güven skoru (0.0-1.0)
        label: Sınıf etiketi
    """
    bbox: Tuple[int, int, int, int]
    score: float
    label: str

    def __post_init__(self) -> None:
        """Validation kontrolü."""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")
        if any(v < 0 for v in self.bbox):
            raise ValueError(f"Bbox values must be non-negative, got {self.bbox}")

    @property
    def area(self) -> int:
        """Bounding box alanını döndürür."""
        return self.bbox[2] * self.bbox[3]

    @property
    def center(self) -> Tuple[int, int]:
        """Bounding box merkez noktasını döndürür."""
        x, y, w, h = self.bbox
        return (x + w // 2, y + h // 2)


@dataclass
class Strawberry:
    """Çilek varlığı (entity).
    
    Attributes:
        id: Takip ID'si (None ise henüz atanmamış)
        detection: Tespit bilgisi
        ripeness: Olgunluk durumu
    """
    id: int | None
    detection: Detection
    ripeness: Ripeness

    def is_tracked(self) -> bool:
        """Çileğin takip edilip edilmediğini kontrol eder."""
        return self.id is not None

    def confidence_level(self) -> str:
        """Güven seviyesini kategorize eder."""
        score = self.detection.score
        if score >= 0.9:
            return "high"
        elif score >= 0.7:
            return "medium"
        return "low"
