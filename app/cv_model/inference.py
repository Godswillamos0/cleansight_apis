from pathlib import Path
from ultralytics import YOLO
import supervision as sv
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "best.pt"

model = YOLO("../cv_model/best.pt")


def run_inference(image_path, model=model):
    results = model.predict(source=image_path, save=False, verbose=False)
    sv_results = sv.Detections.from_ultralytics(results[0])
    bboxes = sv_results.xyxy
    labels = sv_results.data['class_name']

    total_objects_per_class = np.unique(labels, return_counts=True)
    return total_objects_per_class, sv_results


def evaluate_cleanliness(pre_image, post_image):
    pre_classes, _ = run_inference(pre_image)
    post_classes, _ = run_inference(post_image)

    pre_class_names, pre_counts = pre_classes
    post_class_names, post_counts = post_classes

    pre_total = sum(pre_counts) if len(pre_counts) > 0 else 0
    post_total = sum(post_counts) if len(post_counts) > 0 else 0

    total_cleanliness_score = (pre_total - post_total) / pre_total * 100 if pre_total > 0 else 0

    cleanliness_score_per_class = {}
    for cls in np.unique(np.concatenate((pre_class_names, post_class_names))):
        pre_count = pre_counts[pre_class_names == cls].sum() if cls in pre_class_names else 0
        post_count = post_counts[post_class_names == cls].sum() if cls in post_class_names else 0
        score = (pre_count - post_count) / pre_count * 100 if pre_count > 0 else 0
        cleanliness_score_per_class[cls] = score

    return total_cleanliness_score, cleanliness_score_per_class