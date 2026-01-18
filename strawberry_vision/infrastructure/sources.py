from typing import Iterator
import logging

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

logger = logging.getLogger(__name__)


class ImageSource:
    """Tek görüntü kaynağı.
    
    Belirtilen yoldaki görüntüyü bir kez okur ve döndürür.
    """
    
    def __init__(self, image_path: str) -> None:
        self.image_path = image_path
        self._yielded = False

    def __iter__(self) -> Iterator[object]:
        import numpy as np
        if self._yielded:
            logger.warning("ImageSource already consumed")
            return iter(())
        self._yielded = True
        if cv2 is None:
            logger.error("OpenCV not available")
            return iter(())
        try:
            frame = cv2.imread(self.image_path)
            if frame is None:
                logger.error(f"Failed to read image: {self.image_path}")
                return iter(())
            logger.info(f"Loaded image: {self.image_path} (shape: {frame.shape})")
            return iter([frame])
        except Exception as e:
            logger.error(f"Error reading image {self.image_path}: {e}")
            return iter(())


class VideoSource:
    """Video dosyası kaynağı.
    
    Belirtilen video dosyasından frame'leri okur.
    """
    
    def __init__(self, video_path: str, max_frames: int | None = None) -> None:
        self.video_path = video_path
        self.max_frames = max_frames

    def __iter__(self) -> Iterator[object]:
        if cv2 is None:
            logger.error("OpenCV not available")
            return iter(())
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {self.video_path}")
                return iter(())
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            logger.info(f"Video opened: {self.video_path} (fps: {fps}, frames: {total_frames})")
            
            count = 0
            while True:
                if self.max_frames is not None and count >= self.max_frames:
                    logger.info(f"Reached max_frames limit: {self.max_frames}")
                    break
                ok, frame = cap.read()
                if not ok:
                    break
                count += 1
                yield frame
            
            logger.info(f"Processed {count} frames from video")
            cap.release()
        except Exception as e:
            logger.error(f"Error processing video {self.video_path}: {e}")
            return iter(())


class CameraSource:
    """Kamera kaynağı (gerçek zamanlı).
    
    Belirtilen kamera cihazından (varsayılan 0) canlı görüntü akışı okur.
    """
    
    def __init__(self, camera_id: int = 0, max_frames: int | None = None) -> None:
        self.camera_id = camera_id
        self.max_frames = max_frames

    def __iter__(self) -> Iterator[object]:
        if cv2 is None:
            logger.error("OpenCV not available")
            return iter(())
        try:
            cap = cv2.VideoCapture(self.camera_id)
            if not cap.isOpened():
                logger.error(f"Failed to open camera: {self.camera_id}")
                return iter(())
            
            logger.info(f"Camera opened: device {self.camera_id}")
            count = 0
            
            while True:
                if self.max_frames is not None and count >= self.max_frames:
                    logger.info(f"Reached max_frames limit: {self.max_frames}")
                    break
                ok, frame = cap.read()
                if not ok:
                    logger.warning("Failed to read frame from camera")
                    break
                count += 1
                yield frame
            
            logger.info(f"Captured {count} frames from camera")
            cap.release()
        except Exception as e:
            logger.error(f"Error accessing camera {self.camera_id}: {e}")
            return iter(())
