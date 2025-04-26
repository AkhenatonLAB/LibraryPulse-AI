import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import time  
  

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

    previous_centers = {}
    last_cross_times = {}
    cross_counter = 0
    line_x = cameraWidth // 2
    cooldown_seconds = 2

    previous_time = time.time()  # FPS için başlangıç zamanı

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
                        # Soldan sağa geçti
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter = max(cross_counter - 1, 0)
                            last_cross_times[id] = current_time

                    elif prev_center_x > line_x and center_x <= line_x:
                        # Sağdan sola geçti
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter += 1
                            last_cross_times[id] = current_time

                    # Hareket oku çiz
                    cv2.arrowedLine(annotated_frame, (prev_center_x, prev_center_y),
                                    (center_x, center_y), (0, 255, 0), 2, tipLength=0.5)

                    # Hareket yönünü yaz
                    direction = ""
                    dx = center_x - prev_center_x
                    dy = center_y - prev_center_y
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            direction = "Left"
                        else:
                            direction = "Right"
                    else:
                        if dy > 0:
                            direction = "Down"
                        else:
                            direction = "Up"

                    cv2.putText(annotated_frame, f"{direction}", (center_x, center_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                previous_centers[id] = (center_x, center_y)

        # FPS hesapla (işlem sonrası)
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

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

openCameraAndRead()
