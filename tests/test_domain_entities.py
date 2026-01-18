import pytest

from strawberry_vision.domain.entities import Ripeness, Detection, Strawberry


class TestRipeness:
    def test_enum_values(self):
        assert Ripeness.RIPE.value == "ripe"
        assert Ripeness.SEMI_RIPE.value == "semi_ripe"
        assert Ripeness.UNRIPE.value == "unripe"
    
    def test_from_string(self):
        assert Ripeness.from_string("ripe") == Ripeness.RIPE
        assert Ripeness.from_string("SEMI_RIPE") == Ripeness.SEMI_RIPE
        assert Ripeness.from_string("invalid") == Ripeness.UNRIPE


class TestDetection:
    def test_valid_detection(self):
        det = Detection(bbox=(10, 20, 30, 40), score=0.95, label="strawberry")
        assert det.bbox == (10, 20, 30, 40)
        assert det.score == 0.95
        assert det.label == "strawberry"
    
    def test_area_property(self):
        det = Detection(bbox=(0, 0, 10, 20), score=0.9, label="test")
        assert det.area == 200
    
    def test_center_property(self):
        det = Detection(bbox=(10, 10, 20, 20), score=0.9, label="test")
        assert det.center == (20, 20)
    
    def test_invalid_score_raises_error(self):
        with pytest.raises(ValueError):
            Detection(bbox=(0, 0, 10, 10), score=1.5, label="test")
        
        with pytest.raises(ValueError):
            Detection(bbox=(0, 0, 10, 10), score=-0.1, label="test")
    
    def test_negative_bbox_raises_error(self):
        with pytest.raises(ValueError):
            Detection(bbox=(-5, 0, 10, 10), score=0.9, label="test")


class TestStrawberry:
    def test_strawberry_creation(self):
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        s = Strawberry(id=1, detection=det, ripeness=Ripeness.RIPE)
        assert s.id == 1
        assert s.detection == det
        assert s.ripeness == Ripeness.RIPE
    
    def test_is_tracked(self):
        det = Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry")
        s1 = Strawberry(id=1, detection=det, ripeness=Ripeness.RIPE)
        s2 = Strawberry(id=None, detection=det, ripeness=Ripeness.RIPE)
        
        assert s1.is_tracked() is True
        assert s2.is_tracked() is False
    
    def test_confidence_level(self):
        det_high = Detection(bbox=(0, 0, 10, 10), score=0.95, label="strawberry")
        det_medium = Detection(bbox=(0, 0, 10, 10), score=0.8, label="strawberry")
        det_low = Detection(bbox=(0, 0, 10, 10), score=0.5, label="strawberry")
        
        s_high = Strawberry(id=1, detection=det_high, ripeness=Ripeness.RIPE)
        s_medium = Strawberry(id=2, detection=det_medium, ripeness=Ripeness.RIPE)
        s_low = Strawberry(id=3, detection=det_low, ripeness=Ripeness.RIPE)
        
        assert s_high.confidence_level() == "high"
        assert s_medium.confidence_level() == "medium"
        assert s_low.confidence_level() == "low"
