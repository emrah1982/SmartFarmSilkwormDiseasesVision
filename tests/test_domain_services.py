import pytest

from strawberry_vision.domain.entities import Ripeness, Detection, Strawberry
from strawberry_vision.domain.services import TrackingService, CountingService


class TestTrackingService:
    def test_assign_ids(self):
        tracker = TrackingService()
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        
        strawberries = [
            Strawberry(id=None, detection=det, ripeness=Ripeness.RIPE),
            Strawberry(id=None, detection=det, ripeness=Ripeness.SEMI_RIPE),
        ]
        
        result = tracker.assign_ids(strawberries)
        
        assert result[0].id == 1
        assert result[1].id == 2
        assert tracker.total_tracked == 2
    
    def test_reset(self):
        tracker = TrackingService()
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        
        strawberries = [Strawberry(id=None, detection=det, ripeness=Ripeness.RIPE)]
        tracker.assign_ids(strawberries)
        
        assert tracker.total_tracked == 1
        
        tracker.reset()
        assert tracker.total_tracked == 0
        assert tracker._next_id == 1


class TestCountingService:
    def test_count_by_ripeness(self):
        counter = CountingService()
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        
        strawberries = [
            Strawberry(id=1, detection=det, ripeness=Ripeness.RIPE),
            Strawberry(id=2, detection=det, ripeness=Ripeness.RIPE),
            Strawberry(id=3, detection=det, ripeness=Ripeness.SEMI_RIPE),
        ]
        
        counts = counter.count_by_ripeness(strawberries)
        
        assert counts["ripe"] == 2
        assert counts["semi_ripe"] == 1
    
    def test_count_total(self):
        counter = CountingService()
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        
        strawberries = [
            Strawberry(id=1, detection=det, ripeness=Ripeness.RIPE),
            Strawberry(id=2, detection=det, ripeness=Ripeness.UNRIPE),
        ]
        
        assert counter.count_total(strawberries) == 2
    
    def test_count_by_confidence(self):
        counter = CountingService()
        
        det_high = Detection(bbox=(0, 0, 10, 10), score=0.95, label="strawberry")
        det_low = Detection(bbox=(0, 0, 10, 10), score=0.5, label="strawberry")
        
        strawberries = [
            Strawberry(id=1, detection=det_high, ripeness=Ripeness.RIPE),
            Strawberry(id=2, detection=det_low, ripeness=Ripeness.RIPE),
        ]
        
        counts = counter.count_by_confidence(strawberries)
        
        assert counts["high"] == 1
        assert counts["low"] == 1
    
    def test_get_statistics(self):
        counter = CountingService()
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        
        strawberries = [
            Strawberry(id=1, detection=det, ripeness=Ripeness.RIPE),
            Strawberry(id=None, detection=det, ripeness=Ripeness.SEMI_RIPE),
        ]
        
        stats = counter.get_statistics(strawberries)
        
        assert stats["total"] == 2
        assert stats["tracked"] == 1
        assert "by_ripeness" in stats
        assert "by_confidence" in stats
