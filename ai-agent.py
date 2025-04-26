import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import time
import csv
from datetime import datetime
import os  # This is for managing paths and saving the file in the current directory

def write_to_csv(counter, csv_filename):
    # Write only the counter value to the CSV file
    with open(csv_filename, mode="w", newline='') as file:  # overwrite mode
        writer = csv.writer(file)
        writer.writerow([counter])  # Only write the counter value

def openCameraAndRead():
    cameraHeight = int(input("Height: "))
    cameraWidth = int(input("Width: "))
    model = YOLO("yolo11n.pt")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cameraWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraHeight)
    print(f"Resolution {cameraHeight}x{cameraWidth}")

    if not cap.isOpened():
        print("Camera not working")
        exit()

    # Get the current folder path where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))  # This gets the script's directory path
    csv_filename = os.path.join(script_dir, "people_cross_counter.csv")

    # Create CSV initially with the first counter value (0) if it doesn't exist
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode="w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([0])  # Initial count value
        print(f"CSV created at {datetime.now()} in {script_dir}.")

    previous_centers = {}
    last_cross_times = {}
    cross_counter = 0
    line_x = cameraWidth // 2
    cooldown_seconds = 2

    previous_time = time.time()

    # Timer and CSV update interval setup
    start_time = time.time()
    update_interval = 30 * 60

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Image cannot be read or program ended")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model.track(frame, conf=0.3, imgsz=480, persist=True)
        annotated_frame = results[0].plot()

        cv2.line(annotated_frame, (line_x, 0), (line_x, cameraHeight), (255, 0, 255), 2)

        current_time = time.time()

        if hasattr(results[0], 'boxes') and results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy()
            boxes = results[0].boxes.xyxy.cpu().numpy()

            for id, box in zip(ids, boxes):
                x1, y1, x2, y2 = map(int, box)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                if id in previous_centers:
                    prev_center_x, prev_center_y = previous_centers[id]

                    if prev_center_x < line_x and center_x >= line_x:
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter = max(cross_counter - 1, 0)
                            last_cross_times[id] = current_time

                    elif prev_center_x > line_x and center_x <= line_x:
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter += 1
                            last_cross_times[id] = current_time

                    # Draw movement arrow
                    cv2.arrowedLine(annotated_frame, (prev_center_x, prev_center_y),
                                    (center_x, center_y), (0, 255, 0), 2, tipLength=0.5)

                previous_centers[id] = (center_x, center_y)

        # FPS calculation
        new_time = time.time()
        fps = 1 / (new_time - previous_time)
        previous_time = new_time

        cv2.putText(annotated_frame, f"Counter: {cross_counter}", (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(annotated_frame, f"Total: {len(results[0].boxes)}", (15, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (15, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Camera with Walking Direction and Counter", annotated_frame)

        # Every 30 minutes, update the CSV
        if (current_time - start_time) >= update_interval:
            write_to_csv(cross_counter, csv_filename)  # Update CSV with only the counter value
            print(f"CSV updated at {datetime.now()} with counter {cross_counter}")
            start_time = current_time  # Reset timer

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

openCameraAndRead()
