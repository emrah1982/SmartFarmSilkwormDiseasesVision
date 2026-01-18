import argparse

from strawberry_vision.application.pipeline import InferencePipeline
from strawberry_vision.infrastructure.sources import ImageSource, VideoSource
from strawberry_vision.infrastructure.detectors import YOLODetector


def main():
    parser = argparse.ArgumentParser(description="Strawberry Vision Inference")
    parser.add_argument("--image", type=str, default="sample.jpg", help="Tek görüntü yolu")
    parser.add_argument("--video", type=str, default=None, help="Video yolu")
    parser.add_argument("--model", type=str, default=None, help="YOLO model .pt dosya yolu")
    parser.add_argument("--max-frames", type=int, default=None, help="Video için maksimum kare sayısı")
    args = parser.parse_args()

    detector = YOLODetector(model_path=args.model) if args.model else YOLODetector()
    pipeline = InferencePipeline(detector=detector)

    if args.video:
        source = VideoSource(video_path=args.video, max_frames=args.max_frames)
    else:
        source = ImageSource(image_path=args.image)

    for frame in source:
        result = pipeline.run(frame)
        print(result.summary())


if __name__ == "__main__":
    main()
