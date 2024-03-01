from ultralytics import YOLO
import cv2
import math
import cvzone


class ObjectDetection:
    def __init__(self, weights_path, selective_classes):
        self.model = YOLO(weights_path)
        self.class_names = [
            "person",
            "bicycle",
            "car",
            "motorbike",
            "aeroplane",
            "bus",
            "train",
            "truck",
            "boat",
            "traffic light",
            "fire hydrant",
            "stop sign",
            "parking meter",
            "bench",
            "bird",
            "cat",
            "dog",
            "horse",
            "sheep",
            "cow",
            "elephant",
            "bear",
            "zebra",
            "giraffe",
            "backpack",
            "umbrella",
            "handbag",
            "tie",
            "suitcase",
            "frisbee",
            "skis",
            "snowboard",
            "sports ball",
            "kite",
            "baseball bat",
            "baseball glove",
            "skateboard",
            "surfboard",
            "tennis racket",
            "bottle",
            "wine glass",
            "cup",
            "fork",
            "knife",
            "spoon",
            "bowl",
            "banana",
            "apple",
            "sandwich",
            "orange",
            "broccoli",
            "carrot",
            "hot dog",
            "pizza",
            "donut",
            "cake",
            "chair",
            "sofa",
            "pottedplant",
            "bed",
            "diningtable",
            "toilet",
            "tvmonitor",
            "laptop",
            "mouse",
            "remote",
            "keyboard",
            "cell phone",
            "microwave",
            "oven",
            "toaster",
            "sink",
            "refrigerator",
            "book",
            "clock",
            "vase",
            "scissors",
            "teddy bear",
            "hair drier",
            "toothbrush",
        ]
        self.selective_classes = selective_classes
        self.detected_classes = []

    @property
    def detected_vehicle_count(self):
        return len(self.detected_classes)

    def detect_objects(self, img):
        results = self.model(img)
        result = results[0].boxes
        boxes = result.xyxy
        confs = result.conf
        classes = result.cls
        return boxes, confs, classes

    def filter_objects(self, boxes, confs, classes):
        filtered_boxes = []
        filtered_confs = []
        filtered_classes = []

        for i, class_id in enumerate(classes):
            if class_id in self.selective_classes:
                filtered_boxes.append(boxes[i])
                filtered_confs.append(confs[i])
                filtered_classes.append(class_id)

        return filtered_boxes, filtered_confs, filtered_classes

    def detect_and_filter_objects(self, img):
        boxes, confs, classes = self.detect_objects(img)
        filtered_boxes, filtered_confs, filtered_classes = self.filter_objects(
            boxes, confs, classes
        )
        return filtered_boxes, filtered_confs, filtered_classes

    def draw_boxes(self, img, boxes, confs, classes):
        self.detected_classes = []
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            bbox = x1, y1, w, h

            # class name
            cls = int(classes[i])
            # confidence
            conf = math.ceil((confs[i] * 100)) / 100

            # adding detected classname in detected_classes
            self.detected_classes.append(self.class_names[cls])

            # box border
            cvzone.cornerRect(img, bbox, l=10, colorC=(255, 0, 0))
            # class name
            cvzone.putTextRect(
                img,
                f"{self.class_names[cls]} {conf}",
                (max(0, x1), max(35, y1)),
                scale=1.5,
                thickness=2,
                offset=3,
            )
        return img, self.detected_classes


# Example usage
if __name__ == "__main__":
    weights_path = "yolo-weights/yolov8n.pt"
    selective_classes = [2, 3, 5, 7]

    object_detector = ObjectDetection(weights_path, selective_classes)

    # Example usage with OpenCV capture
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        boxes, confidences, class_ids = object_detector.detect_objects(img)
        object_detector.draw_boxes(img, boxes, confidences, class_ids)

        cv2.imshow("Object Detection", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
