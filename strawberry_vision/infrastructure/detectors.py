from typing import List, Tuple

import numpy as np
import yaml
from pathlib import Path

from strawberry_vision.domain.entities import Detection, Ripeness

try:
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover
    YOLO = None  # fallback when ultralytics isn't available


class YOLODetector:
    def __init__(self, model_path: str | None = None) -> None:
        self.model = None
        self.class_names: list[str] = []

        try:
            project_root = Path(__file__).resolve().parents[2]
            data_yaml_path = project_root / 'configs' / 'strawberry_data.yaml'
            if data_yaml_path.exists():
                with open(data_yaml_path, 'r', encoding='utf-8') as f:
                    data_cfg = yaml.safe_load(f) or {}
                    names = data_cfg.get('names')
                    if isinstance(names, list):
                        self.class_names = [str(n) for n in names]
        except Exception:
            self.class_names = []

        if YOLO is not None and model_path:
            try:
                self.model = YOLO(model_path)
            except Exception:
                self.model = None

    def detect(self, frame: np.ndarray) -> List[Detection]:
        if frame is None:
            return []
        if self.model is None:
            # Dummy: no detections when model not loaded
            return []
        try:
            results = self.model.predict(source=frame, verbose=False)
            detections: List[Detection] = []
            for r in results:
                for b in r.boxes:
                    x1, y1, x2, y2 = b.xyxy[0].tolist()
                    w, h = int(x2 - x1), int(y2 - y1)
                    cls_id = int(b.cls[0])
                    label = (
                        self.class_names[cls_id]
                        if 0 <= cls_id < len(self.class_names)
                        else str(cls_id)
                    )
                    det = Detection(bbox=(int(x1), int(y1), w, h), score=float(b.conf[0]), label=label)
                    detections.append(det)
            return detections
        except Exception:
            return []


def classify_ripeness(frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Ripeness:
    x, y, w, h = bbox
    x2, y2 = x + w, y + h
    x, y = max(0, x), max(0, y)
    roi = frame[y:y2, x:x2]
    if roi.size == 0:
        return Ripeness.UNRIPE
    # Simple heuristic: average red channel level
    red_mean = float(np.mean(roi[:, :, 2])) if roi.ndim == 3 and roi.shape[2] >= 3 else 0.0
    if red_mean > 150:
        return Ripeness.RIPE
    if red_mean > 100:
        return Ripeness.SEMI_RIPE
    return Ripeness.UNRIPE
