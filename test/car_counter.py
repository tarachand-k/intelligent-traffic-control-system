import cv2
import cvzone

from test.sort import *
from src import ObjectDetection


def test_video_detection(input_folder="", isLive=False):
    selective_classes = [2, 3, 5, 7]
    limits = [120, 460, 1240, 460]
    crossed_vehicles = []

    weights_path = "../src/yolo-weights/yolov8n.pt"
    object_detector = ObjectDetection(weights_path, selective_classes)

    cap = cv2.VideoCapture(0 if isLive else os.path.join(input_folder, "test.mp4"))
    if isLive:
        cap.set(3, 1280)
        cap.set(4, 700)
    mask = None if isLive else cv2.imread(os.path.join(input_folder, "mask.png"))
    # tracker
    tracker = None if isLive else Sort(max_age=20, min_hits=3, iou_threshold=0.3)
    while True:
        success, img = cap.read()
        img_region = img if isLive else cv2.bitwise_and(img, mask)
        boxes, confidences, class_ids = object_detector.detect_objects(img_region)
        object_detector.draw_boxes(img, boxes, confidences, class_ids)

        if not isLive:
            graphic_img = cv2.imread(os.path.join(input_folder, "graphics.png"), cv2.IMREAD_UNCHANGED)
            img = cvzone.overlayPNG(img, graphic_img, (0, 0))
            detections = np.empty((0, 5))

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                current_detection = np.array([x1, y1, x2, y2, confidences[i]])
                detections = np.vstack((detections, current_detection))

            cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), 3)
            tracker_results = tracker.update(detections)

            for result in tracker_results:
                x1, y1, x2, y2, Id = result
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if limits[0] < cx < limits[2] and limits[1] - 30 < cy < limits[1] + 30:
                    if crossed_vehicles.count(Id) == 0:
                        crossed_vehicles.append(Id)
            cv2.line(
                    img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 3
                )
            cvzone.putTextRect(
                img,
                str(len(crossed_vehicles)),
                (155, 60),
                thickness=5,
                scale=3,
                colorR=(255, 233, 193),
                colorT=(255, 0, 0),
                offset=0,
            )

        cv2.imshow("Object Detection", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_video_detection("../input")
