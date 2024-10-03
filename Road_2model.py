import torch
import cv2
from io import BytesIO
import os
from datetime import datetime

class HoldDetector:
    def __init__(self, model_path_hole='models/holedetect.pt', model_path_road='/home/tunz/Documents/black-hole-detection-device-main/models/Roaddetectv2.5.pt'):
        # Load the model for detecting holes
        self.model_hole = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path_hole, force_reload=True)
        self.model_hole.eval()

        # Load the model for detecting road types
        self.model_road = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path_road, force_reload=True)
        self.model_road.eval()

    def detect_objects(self, frame):
        height, width = frame.shape[:2]
        center_y = height // 2

        roi_y1 = center_y - 200
        roi_y2 = center_y + 200

        roi = frame[roi_y1:roi_y2, 0:width]

        # Detect holes in the region of interest (ROI)
        results_hole = self.model_hole(roi)
        hole_data = []
        for det in results_hole.xyxy[0]:
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

            hole_data.append({
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'confidence': float(conf),
                'class': int(cls),
                'size_hole': size_category
            })

        # Detect road types in the entire frame
        results_road = self.model_road(frame)
        road_data = []
        class_names = ['Road_ASPHALT', 'Road_CONCRETE']
        for det in results_road.xyxy[0]:
            x1, y1, x2, y2, conf, cls = det
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            road_data.append({
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'confidence': float(conf),
                'class': int(cls),
                'road_type': class_names[int(cls)]  # Use actual class names
            })

        return roi, hole_data, road_data


if __name__ == "__main__":
    # Initialize the webcam
    cap = cv2.VideoCapture("/home/tunz/PycharmProjects/Road_linux/vidieo/C0014.MP4")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Initialize the detector with the model paths
    detector = HoldDetector(model_path_hole='models/holedetect.pt', model_path_road='/home/tunz/Documents/black-hole-detection-device-main/models/Roaddetectv2.5.pt')

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Detect holes and road types in the frame
        roi, hole_detections, road_detections = detector.detect_objects(frame)

        # Draw bounding boxes and labels for holes on the frame
        for detection in hole_detections:
            cv2.rectangle(roi, (detection['x1'], detection['y1']), (detection['x2'], detection['y2']), (0, 255, 0), 2)
            label = f"Hole: {detection['size_hole']} ({detection['confidence']:.2f})"
            cv2.putText(roi, label, (detection['x1'], detection['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Draw bounding boxes and labels for road types on the frame
        for detection in road_detections:
            # Reduce the thickness and size of the bounding box
            cv2.rectangle(frame, (detection['x1'], detection['y1']), (detection['x2'], detection['y2']), (255, 0, 0), 1)  # Reduced thickness
            label = f"Road: {detection['road_type']} ({detection['confidence']:.2f})"
            cv2.putText(frame, label, (detection['x1'], detection['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)  # Reduced font size

        # Save the image when detection is found
        if hole_detections or road_detections:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_name = f"{timestamp}.jpg"
            cv2.imwrite(os.path.join('img_output2', img_name), frame)
            print(f"Image saved: {img_name}")

        # Display the resulting frame
        cv2.imshow('Webcam Object Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()
