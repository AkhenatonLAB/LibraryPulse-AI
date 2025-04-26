import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO

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

    # Kişilerin ID -> merkez konumları tutmak için dictionary
    previous_centers = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Image cannot be read or program ended")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # YOLO ile tespit ve takip yap
        results = model.track(frame, conf=0.5, imgsz=480, persist=True)
        annotated_frame = results[0].plot()

        # Eğer id bilgileri yoksa, tracking çalışmamış demektir
        if hasattr(results[0], 'boxes') and results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy()
            boxes = results[0].boxes.xyxy.cpu().numpy()

            for id, box in zip(ids, boxes):
                x1, y1, x2, y2 = map(int, box)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # ID daha önce görüldüyse hareket yönünü hesapla
                if id in previous_centers:
                    prev_center = previous_centers[id]
                    dx = center_x - prev_center[0]
                    dy = center_y - prev_center[1]

                    # Hareket vektörünü çiz
                    cv2.arrowedLine(annotated_frame, prev_center, (center_x, center_y), (0, 255, 0), 2, tipLength=0.5)

                    # İsteğe bağlı: dx, dy değerine göre yön ismi yazdırabilirsin
                    direction = ""
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

                # Şu anki merkezi kaydet
                previous_centers[id] = (center_x, center_y)

        # Görüntüleri göster
        cv2.putText(annotated_frame, f"Total: {len(results[0].boxes)}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow("Camera with Walking Direction", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

openCameraAndRead()
