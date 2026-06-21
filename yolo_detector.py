from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

def detect(image_path, save_path):

    results = model(image_path)
    result = results[0]

    img = result.plot()
    cv2.imwrite(save_path, img)

    names = result.names
    boxes = result.boxes.cls.cpu().numpy()

    stats = {}

    for c in boxes:
        label = names[int(c)]
        stats[label] = stats.get(label, 0) + 1

    return stats