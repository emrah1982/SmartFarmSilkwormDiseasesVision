import numpy as np

from strawberry_vision.application.pipeline import InferencePipeline
from strawberry_vision.domain.entities import Detection


class FakeDetector:
    def detect(self, frame: np.ndarray):
        # Three detections with different regions for ripeness heuristic
        return [
            Detection(bbox=(0, 0, 10, 10), score=0.9, label="strawberry"),
            Detection(bbox=(20, 0, 10, 10), score=0.8, label="strawberry"),
            Detection(bbox=(30, 0, 10, 10), score=0.7, label="strawberry"),
        ]


def build_frame() -> np.ndarray:
    frame = np.zeros((40, 40, 3), dtype=np.uint8)
    # RIPE region (red mean > 150)
    frame[0:10, 0:10, 2] = 200
    # SEMI_RIPE region (100 < red mean <= 150)
    frame[0:10, 20:30, 2] = 120
    # UNRIPE region (red mean <= 100)
    frame[0:10, 30:40, 2] = 50
    return frame


def main():
    pipeline = InferencePipeline(detector=FakeDetector())
    frame = build_frame()
    result = pipeline.run(frame)
    counts = result.summary()
    assert counts.get("ripe", 0) == 1, counts
    assert counts.get("semi_ripe", 0) == 1, counts
    assert counts.get("unripe", 0) == 1, counts
    print("Smoke test OK:", counts)


if __name__ == "__main__":
    main()
