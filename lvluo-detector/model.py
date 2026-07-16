import os
import numpy as np
from PIL import Image

os.environ['PYTHONUTF8'] = '1'

from ultralytics import YOLO

CLASS_CN = {'healthy': '健康', 'unhealthy': '不健康'}


class LeafDetector:
    def __init__(self, model_path='best.pt'):
        self.model = YOLO(model_path)

    def predict(self, image, conf=0.25):
        results = self.model.predict(image, imgsz=640, conf=conf, verbose=False)
        result = results[0]

        annotated = result.plot()
        annotated_pil = Image.fromarray(annotated[..., ::-1])

        detections = []
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_en = self.model.names[cls_id]
                confidence = float(box.conf[0])
                detections.append({
                    'class': cls_en,
                    'class_cn': CLASS_CN.get(cls_en, cls_en),
                    'confidence': round(confidence, 3),
                })

        return annotated_pil, detections
