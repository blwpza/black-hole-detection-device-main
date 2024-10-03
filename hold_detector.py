import torch
import cv2
from io import BytesIO
import os
from datetime import datetime

class HoldDetector:
    def __init__(self, model_path='models/holedetect.pt'):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
        self.model.eval()

    def detect_objects(self, frame):
        height, width = frame.shape[:2]
        center_y = height // 2

        roi_y1 = center_y - 300
        roi_y2 = center_y + 300

        roi = frame[roi_y1:roi_y2, 0:width]
        results = self.model(roi)
        # cv2.rectangle( frame, (0, roi_y1), (width, roi_y2), (255, 0, 0), 2)
        try:
            data = []
            for det in results.xyxy[0]:
                x1, y1, x2, y2, conf, cls = det

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                diagonal_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                size_percentage = (diagonal_length / 600) * 100

                if size_percentage < 33:
                    size_category = "Small"
                elif size_percentage < 66:
                    size_category = "Medium"
                else:
                    size_category = "Large"

                data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'confidence': float(conf),
                    'class': int(cls),
                    'size_hole': size_category
                })

            return roi, data
        except Exception as e:
            return []


if __name__ == "__main__":
    # Initialize the webcam
    cap = cv2.VideoCapture("/home/tunz/PycharmProjects/Road_linux/vidieo/C0014.MP4")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Initialize the detector with the model path
    detector = HoldDetector(model_path='models/holedetect.pt')

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Detect objects in the frame
        roi, detections = detector.detect_objects(frame)

        # Draw bounding boxes and labels on the frame
        for detection in detections:
            cv2.rectangle(roi, (detection['x1'], detection['y1']), (detection['x2'], detection['y2']), (0, 255, 0), 2)
            label = f"{detection['size_hole']} ({detection['confidence']:.2f})"
            cv2.putText(roi, label, (detection['x1'], detection['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Save the image when detection is found
        if detections:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_name = f"{timestamp}.jpg"
            cv2.imwrite(os.path.join('img_output', img_name), frame)
            print(f"Image saved: {img_name}")

        # Display the resulting frame
        cv2.imshow('Webcam Object Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()