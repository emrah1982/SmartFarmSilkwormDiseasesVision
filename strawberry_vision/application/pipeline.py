from dataclasses import dataclass, field
from typing import Dict, List
import logging
import time

import numpy as np

from strawberry_vision.domain.entities import Strawberry
from strawberry_vision.domain.services import TrackingService, CountingService
from strawberry_vision.infrastructure.detectors import YOLODetector, classify_ripeness
from strawberry_vision.presentation.visualizer import Visualizer

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Pipeline çalıştırma sonucu.
    
    Attributes:
        counts: Olgunluk durumuna göre sayım
        total: Toplam çilek sayısı
        statistics: Detaylı istatistikler
        processing_time: İşlem süresi (saniye)
        frame_processed: İşlenen frame sayısı
    """
    counts: Dict[str, int]
    total: int = 0
    statistics: Dict[str, any] = field(default_factory=dict)
    processing_time: float = 0.0
    frame_processed: int = 0

    def summary(self) -> Dict[str, any]:
        """Özet bilgileri döndürür."""
        return {
            "counts": self.counts,
            "total": self.total,
            "processing_time": round(self.processing_time, 3),
            "frames": self.frame_processed,
        }


class InferencePipeline:
    """Ana inference pipeline.
    
    Detection → Classification → Tracking → Counting → Visualization akışını yönetir.
    """
    
    def __init__(
        self,
        detector: YOLODetector | None = None,
        tracker: TrackingService | None = None,
        counter: CountingService | None = None,
        visualizer: Visualizer | None = None,
        enable_logging: bool = True,
    ) -> None:
        self.detector = detector or YOLODetector()
        self.tracker = tracker or TrackingService()
        self.counter = counter or CountingService()
        self.visualizer = visualizer or Visualizer()
        self.enable_logging = enable_logging
        self._frame_count = 0
        self._total_processing_time = 0.0
        
        if self.enable_logging:
            logger.info("InferencePipeline initialized")

    def run(self, frame: np.ndarray) -> PipelineResult:
        """Tek bir frame üzerinde pipeline çalıştırır.
        
        Args:
            frame: İşlenecek görüntü frame'i
            
        Returns:
            Pipeline sonuç nesnesi
        """
        start_time = time.time()
        self._frame_count += 1
        
        try:
            # Detection
            detections = self.detector.detect(frame)
            if self.enable_logging:
                logger.debug(f"Detected {len(detections)} objects")
            
            # Classification
            strawberries: List[Strawberry] = []
            for det in detections:
                ripeness = classify_ripeness(frame, det.bbox)
                strawberries.append(Strawberry(id=None, detection=det, ripeness=ripeness))
            
            # Tracking
            strawberries = self.tracker.assign_ids(strawberries)
            
            # Counting
            counts = self.counter.count_by_ripeness(strawberries)
            statistics = self.counter.get_statistics(strawberries)
            
            # Visualization
            _ = self.visualizer.draw(frame, strawberries)
            
            processing_time = time.time() - start_time
            self._total_processing_time += processing_time
            
            if self.enable_logging:
                logger.info(f"Frame {self._frame_count}: {len(strawberries)} strawberries, {processing_time:.3f}s")
            
            return PipelineResult(
                counts=counts,
                total=len(strawberries),
                statistics=statistics,
                processing_time=processing_time,
                frame_processed=self._frame_count,
            )
        except Exception as e:
            logger.error(f"Pipeline error on frame {self._frame_count}: {e}")
            return PipelineResult(
                counts={},
                total=0,
                processing_time=time.time() - start_time,
                frame_processed=self._frame_count,
            )
    
    def get_metrics(self) -> Dict[str, any]:
        """Pipeline metriklerini döndürür."""
        avg_time = self._total_processing_time / self._frame_count if self._frame_count > 0 else 0.0
        return {
            "total_frames": self._frame_count,
            "total_time": round(self._total_processing_time, 3),
            "avg_time_per_frame": round(avg_time, 3),
            "fps": round(1.0 / avg_time, 2) if avg_time > 0 else 0.0,
            "total_tracked": self.tracker.total_tracked,
        }
    
    def reset(self) -> None:
        """Pipeline durumunu sıfırlar."""
        self._frame_count = 0
        self._total_processing_time = 0.0
        self.tracker.reset()
        if self.enable_logging:
            logger.info("Pipeline reset")
