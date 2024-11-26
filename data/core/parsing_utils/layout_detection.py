import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import logging
import threading
import glob


from data.core.parsing_utils.caption import CaptioningModel


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LayoutDetector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_path, conf_threshold=0.2, iou_threshold=0.8):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LayoutDetector, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path, conf_threshold=0.2, iou_threshold=0.8):
        if self._initialized:
            return
        self.model = YOLO(model_path)
        self.class_names = self.model.names
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        logging.debug(f"YOLO model loaded from {model_path}")
        self._initialized = True

        
        self.captioning_model = CaptioningModel()

    def detect_layout(self, image):
        try:
            results = self.model(image, conf=self.conf_threshold, iou=self.iou_threshold)[0]
            detections = sv.Detections.from_ultralytics(results)
            logging.debug(f"Detected {len(detections)} layout elements")
            return detections
        except Exception as e:
            logging.error(f"Layout detection failed: {e}")
            return sv.Detections.empty()

    def get_class_name(self, class_id):
        try:
            return self.class_names[class_id]
        except IndexError:
            logging.error(f"Invalid class ID: {class_id}")
            return "Unknown"

    def caption_image(self, image):
        return self.captioning_model.caption(image)


def _initialize_detector():
    model_path = glob.glob("data/models/*.pt")[0]  
    return LayoutDetector(model_path=model_path)

_layout_detector = _initialize_detector()

def detect_layout(image):
    return _layout_detector.detect_layout(image)

def get_class_name(class_id):
    return _layout_detector.get_class_name(class_id)

def caption_image(image):
    return _layout_detector.caption_image(image)
