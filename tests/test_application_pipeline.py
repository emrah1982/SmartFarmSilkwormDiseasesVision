import numpy as np
import pytest

from strawberry_vision.application.pipeline import InferencePipeline, PipelineResult
from strawberry_vision.domain.entities import Detection, Ripeness


class FakeDetector:
    def detect(self, frame):
        return [
            Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry"),
            Detection(bbox=(20, 20, 10, 10), score=0.8, label="strawberry"),
        ]


class TestPipelineResult:
    def test_summary(self):
        result = PipelineResult(
            counts={"ripe": 2, "semi_ripe": 1},
            total=3,
            processing_time=0.123,
            frame_processed=1,
        )
        
        summary = result.summary()
        
        assert summary["total"] == 3
        assert summary["counts"]["ripe"] == 2
        assert summary["processing_time"] == 0.123
        assert summary["frames"] == 1


class TestInferencePipeline:
    def test_pipeline_run(self):
        pipeline = InferencePipeline(detector=FakeDetector(), enable_logging=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = pipeline.run(frame)
        
        assert result.total == 2
        assert result.frame_processed == 1
        assert result.processing_time > 0
    
    def test_get_metrics(self):
        pipeline = InferencePipeline(detector=FakeDetector(), enable_logging=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        pipeline.run(frame)
        pipeline.run(frame)
        
        metrics = pipeline.get_metrics()
        
        assert metrics["total_frames"] == 2
        assert metrics["total_time"] > 0
        assert metrics["fps"] > 0
    
    def test_reset(self):
        pipeline = InferencePipeline(detector=FakeDetector(), enable_logging=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        pipeline.run(frame)
        assert pipeline._frame_count == 1
        
        pipeline.reset()
        assert pipeline._frame_count == 0
        assert pipeline._total_processing_time == 0.0
