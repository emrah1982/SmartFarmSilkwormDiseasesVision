from collections import Counter
from typing import Dict, List

from .entities import Strawberry, Ripeness


class TrackingService:
    """Çilek takip servisi.
    
    Her çileğe benzersiz ID atar ve frame'ler arası takibi sağlar.
    Basit ID atama stratejisi kullanır (gelişmiş tracking için ByteTrack/DeepSORT entegre edilebilir).
    """
    
    def __init__(self) -> None:
        self._next_id = 1
        self._tracked_count = 0

    def assign_ids(self, strawberries: List[Strawberry]) -> List[Strawberry]:
        """Çileklere ID atar.
        
        Args:
            strawberries: ID atanacak çilek listesi
            
        Returns:
            ID'leri atanmış çilek listesi
        """
        for s in strawberries:
            if s.id is None:
                s.id = self._next_id
                self._next_id += 1
                self._tracked_count += 1
        return strawberries

    def reset(self) -> None:
        """Tracking durumunu sıfırlar."""
        self._next_id = 1
        self._tracked_count = 0

    @property
    def total_tracked(self) -> int:
        """Toplam takip edilen çilek sayısını döndürür."""
        return self._tracked_count


class CountingService:
    """Çilek sayım servisi.
    
    Olgunluk durumuna göre çilekleri sayar ve istatistik üretir.
    """
    
    def count_by_ripeness(self, strawberries: List[Strawberry]) -> Dict[str, int]:
        """Olgunluk durumuna göre çilekleri sayar.
        
        Args:
            strawberries: Sayılacak çilek listesi
            
        Returns:
            Olgunluk durumlarına göre sayım dictionary'si
        """
        c = Counter(s.ripeness.value for s in strawberries)
        return {k: int(v) for k, v in c.items()}

    def count_total(self, strawberries: List[Strawberry]) -> int:
        """Toplam çilek sayısını döndürür."""
        return len(strawberries)

    def count_by_confidence(self, strawberries: List[Strawberry]) -> Dict[str, int]:
        """Güven seviyesine göre çilekleri sayar."""
        c = Counter(s.confidence_level() for s in strawberries)
        return {k: int(v) for k, v in c.items()}

    def get_statistics(self, strawberries: List[Strawberry]) -> Dict[str, any]:
        """Detaylı istatistik üretir.
        
        Returns:
            total: Toplam çilek sayısı
            by_ripeness: Olgunluk durumuna göre dağılım
            by_confidence: Güven seviyesine göre dağılım
            tracked: Takip edilen çilek sayısı
        """
        return {
            "total": self.count_total(strawberries),
            "by_ripeness": self.count_by_ripeness(strawberries),
            "by_confidence": self.count_by_confidence(strawberries),
            "tracked": sum(1 for s in strawberries if s.is_tracked()),
        }
